
import os
import sys
import requests
from dotenv import load_dotenv
from atlassian import Jira

load_dotenv()

# Configuration matches jira_tool.py
JIRA_URL = os.getenv("JIRA_URL")
USERNAME = os.getenv("JIRA_USER_EMAIL")
API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = "SCRUM"
FEATURE_NAME = "Feature: Product Search"

def main():
    print("--- Advanced Xray POC (via atlassian lib) ---")
    
    if not all([JIRA_URL, USERNAME, API_TOKEN]):
        print("ERROR: Missing env vars (JIRA_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN)")
        return

    try:
        jira = Jira(
            url=JIRA_URL,
            username=USERNAME,
            password=API_TOKEN,
            cloud=True
        )
        
        # 1. Get Project Issue Types
        print(f"\n1. Fetching Issue Types for Project '{PROJECT_KEY}'...")
        # The library method get_project_issue_types might not exist directly, using raw API via library
        project = jira.project(PROJECT_KEY)
        if not project:
             print(f"ERROR: Project {PROJECT_KEY} not found.")
             return
             
        issue_types = project.get('issueTypes', [])
        print(f"Found {len(issue_types)} issue types:")
        
        test_set_id = None
        pre_cond_id = None
        
        for t in issue_types:
            print(f" - ID: {t['id']}, Name: '{t['name']}'")
            if t['name'] in ['Test Set', 'Test-Set']:
                test_set_id = t['id']
            elif t['name'] in ['Pre-Condition', 'Pre-condition', 'Test Pre-Condition']:
                pre_cond_id = t['id']
        
        print(f"\nResult -> Test Set ID: {test_set_id}, Pre-Condition ID: {pre_cond_id}")
        
        if not test_set_id:
             print("CRITICAL: 'Test-Set' not found. Check spelling.")
             return

        # 2. Search/Create Test Set
        print("\n2. Managing Test Set...")
        jql = f'project = {PROJECT_KEY} AND summary ~ "\\"{FEATURE_NAME}\\"" AND issuetype = "Test-Set"'
        issues = jira.jql(jql).get('issues', [])
        
        test_set_id_val = None
        if issues:
            test_set_key = issues[0]['key']
            test_set_id_val = issues[0]['id']
            print(f"Found existing Test Set: {test_set_key} (ID: {test_set_id_val})")
        else:
            print("Creating new Test Set...")
            new_issue = jira.issue_create(
                fields={
                    "project": {"key": PROJECT_KEY},
                    "summary": FEATURE_NAME,
                    "description": "Container for features",
                    "issuetype": {"id": test_set_id}
                }
            )
            test_set_key = new_issue['key']
            test_set_id_val = new_issue['id']
            print(f"Created Test Set: {test_set_key} (ID: {test_set_id_val})")
            
        # 3. Pre-Condition
        pre_cond_id_val = None
        if pre_cond_id:
            print("\n3. Managing Pre-Condition...")
            bg_summary = f"{FEATURE_NAME} - Background"
            jql_bg = f'project = {PROJECT_KEY} AND summary ~ "\\"{bg_summary}\\"" AND issuetype = "{pre_cond_id}"'
            issues_bg = jira.jql(jql_bg).get('issues', [])
            
            if issues_bg:
                pre_cond_id_val = issues_bg[0]['id']
                print(f"Found Pre-Condition: {issues_bg[0]['key']} (ID: {pre_cond_id_val})")
            else:
                 print("Creating Pre-Condition...")
                 new_bg = jira.issue_create(
                    fields={
                        "project": {"key": PROJECT_KEY},
                        "summary": bg_summary,
                        "description": "Background steps...",
                        "issuetype": {"id": pre_cond_id}
                    }
                )
                 pre_cond_id_val = new_bg['id']
                 print(f"Created Pre-Condition: {new_bg['key']} (ID: {pre_cond_id_val})")

    except Exception as e:
        print(f"EXCEPTION: {e}")

    # 4. Debug Link Types
    print("\n4. Listing Link Types...")
    try:
        link_types = jira.get_issue_link_types()
        for lt in link_types:
            print(f" - Name: '{lt['name']}', Outward: '{lt['outward']}', Inward: '{lt['inward']}'")
    except Exception as e:
        print(f"Exception listing links: {e}")

    # 5. Test Xray GraphQL Linking
    print("\n5. Testing Xray GraphQL Linking...")
    client_id = os.getenv("XRAY_CLIENT_ID")
    client_secret = os.getenv("XRAY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("Skipping Xray Link test (Missing Xray Credentials)")
        return

    # Get Token
    auth_url = "https://xray.cloud.getxray.app/api/v2/authenticate"
    token_resp = requests.post(auth_url, json={"client_id": client_id, "client_secret": client_secret})
    if token_resp.status_code != 200:
        print(f"Xray Auth Failed: {token_resp.text}")
        return
    token = token_resp.text.replace('"', '')
    print("Xray Auth Success.")

    # GraphQL Mutation
    # Linking SCRUM-36 (Existing Test) to Test Set (SCRUM-49) and Pre-Condition (SCRUM-50)
    # Create a new Test issue to be sure
    print("Creating new Test issue for linking...")
    test_issue_type_id = None
    for t in issue_types: # Reusing the list from step 1
        if t['name'] == 'Test':
            test_issue_type_id = t['id']
            break
            
    if not test_issue_type_id:
        print("CRITICAL: 'Test' issue type not found.")
        return

    new_test = jira.issue_create(
        fields={
            "project": {"key": PROJECT_KEY},
            "summary": "Test for Linking POC",
            "description": "Dummy test",
            "issuetype": {"id": test_issue_type_id}
        }
    )
    test_key = new_test['key']
    test_id_val = new_test['id']
    print(f"Created Test: {test_key} (ID: {test_id_val})")

    graphql_url = "https://xray.cloud.getxray.app/api/v2/graphql"
    headers = {"Authorization": f"Bearer {token}"}
    
    # Mutation 1: Add to Test Set
    mutation_test_set = f"""
    mutation {{
        addTestsToTestSet(
            issueId: "{test_set_id_val}",
            testIssueIds: ["{test_id_val}"]
        ) {{
            addedTests
            warning
        }}
    }}
    """
    
    print(f"Linking {test_key} (ID: {test_id_val}) to Test Set (ID: {test_set_id_val})...")
    resp_ts = requests.post(graphql_url, json={"query": mutation_test_set}, headers=headers)
    print(f"Response: {resp_ts.text}")

    # Mutation 2: Add to Pre-Condition
    if pre_cond_id_val:
        mutation_pre_cond = f"""
        mutation {{
            addTestsToPrecondition(
                issueId: "{pre_cond_id_val}",
                testIssueIds: ["{test_id_val}"]
            ) {{
                addedTests
                warning
            }}
        }}
        """
        
        print(f"Linking {test_key} (ID: {test_id_val}) to Pre-Condition (ID: {pre_cond_id_val})...")
        resp_pc = requests.post(graphql_url, json={"query": mutation_pre_cond}, headers=headers)
        print(f"Response: {resp_pc.text}")

    
if __name__ == "__main__":
    main()
