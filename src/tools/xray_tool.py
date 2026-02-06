import requests
import os
import re
from crewai.tools import BaseTool
from typing import Type, List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from atlassian import Jira

load_dotenv()

class XrayImportInput(BaseModel):
    """Input for XrayImportTool."""
    gherkin_content: str = Field(..., description="The content of the Gherkin .feature file to import.")
    test_key: str = Field(None, description="The Jira key of the Test issue to update (optional).")
    project_key: str = Field(None, description="The key of the Jira project where the test will be created.")

class XrayImportTool(BaseTool):
    name: str = "import_gherkin_to_xray"
    description: str = "Imports Gherkin scenarios into Xray Cloud, links them to Test Sets (Feature) and Pre-Conditions (Background)."
    args_schema: Type[BaseModel] = XrayImportInput

    def _get_xray_token(self):
        client_id = os.getenv("XRAY_CLIENT_ID")
        client_secret = os.getenv("XRAY_CLIENT_SECRET")
        url = "https://xray.cloud.getxray.app/api/v2/authenticate"
        resp = requests.post(url, json={"client_id": client_id, "client_secret": client_secret})
        resp.raise_for_status()
        return resp.text.replace('"', '')

    def _get_jira_client(self):
        return Jira(
            url=os.getenv("JIRA_URL"),
            username=os.getenv("JIRA_USER_EMAIL"),
            password=os.getenv("JIRA_API_TOKEN"),
            cloud=True
        )

    def _find_issue_type_id(self, jira, project_key, type_name):
        project = jira.project(project_key)
        for t in project.get('issueTypes', []):
            if t['name'].lower() == type_name.lower():
                return t['id']
            # Fallback for common variations
            if type_name == "Pre-Condition" and t['name'] in ["Pre-condition", "Test Pre-Condition"]:
                 return t['id']
            if type_name == "Test Set" and t['name'] == "Test-Set":
                 return t['id']
            if type_name == "Test-Set" and t['name'] == "Test Set":
                 return t['id']
        return None

    def _get_or_create_container(self, jira, project_key, summary, description, type_name_variations):
        # 1. Resolve Type ID
        type_id = None
        used_type_name = ""
        for name in type_name_variations:
            type_id = self._find_issue_type_id(jira, project_key, name)
            if type_id:
                used_type_name = name
                break
        
        if not type_id:
            print(f"[XRAY TOOL] WARNING: Issue Type '{type_name_variations[0]}' not found in project {project_key}. Skipping container creation.")
            return None, None

        # 2. Search Existing
        jql = f'project = {project_key} AND summary ~ "\\"{summary}\\"" AND issuetype = "{used_type_name}"'
        issues = jira.jql(jql).get('issues', [])
        if issues:
            print(f"[XRAY TOOL] Found existing {used_type_name}: {issues[0]['key']}")
            return issues[0]['key'], issues[0]['id']

        # 3. Create New
        print(f"[XRAY TOOL] Creating new {used_type_name}: {summary}")
        try:
            new_issue = jira.issue_create(
                fields={
                    "project": {"key": project_key},
                    "summary": summary,
                    "description": description,
                    "issuetype": {"id": type_id}
                }
            )
            return new_issue['key'], new_issue['id']
        except Exception as e:
            print(f"[XRAY TOOL] Error creating {used_type_name}: {e}")
            return None, None

    def _link_tests_graphql(self, token, test_ids: List[str], container_id: str, mutation_field: str):
        if not container_id or not test_ids:
            return

        url = "https://xray.cloud.getxray.app/api/v2/graphql"
        headers = {"Authorization": f"Bearer {token}"}
        
        # Xray GraphQL expects list of strings for IDs
        ids_formatted = ", ".join([f'"{tid}"' for tid in test_ids])
        
        query = f"""
        mutation {{
            {mutation_field}(
                issueId: "{container_id}",
                testIssueIds: [{ids_formatted}]
            ) {{
                addedTests
                warning
            }}
        }}
        """
        response = requests.post(url, json={"query": query}, headers=headers)
        if response.status_code == 200:
            print(f"[XRAY TOOL] Linked tests {test_ids} to container {container_id} ({mutation_field}). Response: {response.text}")
        else:
            print(f"[XRAY TOOL] Error linking tests: {response.text}")


    def _run(self, gherkin_content: str, test_key: str = None, project_key: str = None) -> str:
        try:
            # 1. Parse Gherkin
            feature_match = re.search(r'Feature:\s*(.+)', gherkin_content)
            feature_name = feature_match.group(1).strip() if feature_match else "Unknown Feature"
            has_background = "Background:" in gherkin_content

            print(f"[XRAY TOOL] Processing Feature: '{feature_name}', Has Background: {has_background}")

            # 2. Prepare Context (Test Set & Pre-Condition)
            jira = self._get_jira_client()
            test_set_id = None
            pre_cond_id = None
            
            if project_key:
                # Test Set (Feature)
                _, test_set_id = self._get_or_create_container(
                    jira, project_key, feature_name, 
                    description="Automatically created by CrewAI", 
                    type_name_variations=["Test-Set", "Test Set"]
                )
                
                # Pre-Condition (Background)
                if has_background:
                     bg_summary = f"{feature_name} - Background"
                     _, pre_cond_id = self._get_or_create_container(
                        jira, project_key, bg_summary,
                        description="Shared background steps.",
                        type_name_variations=["Pre-Condition", "Pre-condition", "Test Pre-Condition"]
                     )

            # 3. Import Gherkin (Create Tests)
            token = self._get_xray_token()
            import_url = "https://xray.cloud.getxray.app/api/v2/import/feature"
            headers = {'Authorization': f'Bearer {token}'}
            files = {'file': ('test.feature', gherkin_content, 'text/plain')}
            params = {}
            if test_key: params['testKey'] = test_key
            if project_key: params['projectKey'] = project_key

            print(f"[XRAY TOOL] Importing Gherkin to Project: {project_key}...")
            response = requests.post(import_url, headers=headers, files=files, params=params)
            
            if response.status_code == 200:
                result_json = response.json()
                created_tests = result_json.get('updatedOrCreatedTests', [])
                test_keys = [t.get('key') for t in created_tests]
                test_ids = [str(t.get('id')) for t in created_tests]
                
                # 4. Link Tests
                if test_ids:
                    if test_set_id:
                        self._link_tests_graphql(token, test_ids, test_set_id, "addTestsToTestSet")
                    if pre_cond_id:
                        self._link_tests_graphql(token, test_ids, pre_cond_id, "addTestsToPrecondition")
                
                # Construct JSON-like output for the next agent
                output_mapping = {
                    "test_set": test_set_id,  # ID used for linking, typically ID but could be Key depending on logic
                    "pre_condition": pre_cond_id,
                    "tests": [{"key": t.get('key'), "id": t.get('id')} for t in created_tests]
                }
                
                # We return a formatted string that looks like JSON to be easily parsed by the LLM
                import json
                return json.dumps(output_mapping, indent=2)
            elif response.status_code == 500:
                 return f"Erreur Xray (500) - Potentiel faux positif. Vérifiez manuellement. Réponse: {response.text}"
            else:
                return f"Erreur Xray ({response.status_code}): {response.text}"

        except Exception as e:
            return f"Error in Xray Tool: {str(e)}"
