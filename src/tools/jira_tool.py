from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from atlassian import Jira
import os
from dotenv import load_dotenv

load_dotenv()

class JiraIssueInput(BaseModel):
    """Input for JiraIssueTool."""
    issue_key: str = Field(..., description="The key of the Jira issue (e.g., 'PROJECT-123').")

class JiraIssueTool(BaseTool):
    name: str = "fetch_jira_issue"
    description: str = "Fetches the title, description, and comments of a Jira issue given its key."
    args_schema: Type[BaseModel] = JiraIssueInput

    def _run(self, issue_key: str) -> str:
        try:
            jira = Jira(
                url=os.getenv("JIRA_URL"),
                username=os.getenv("JIRA_USER_EMAIL"),
                password=os.getenv("JIRA_API_TOKEN"),
                cloud=True
            )
            
            issue = jira.issue(issue_key)
            
            title = issue.get('fields', {}).get('summary', 'N/A')
            description = issue.get('fields', {}).get('description', 'N/A')
            project_key = issue.get('fields', {}).get('project', {}).get('key', 'N/A')
            
            # Formater le résultat
            result = f"Projet: {project_key}\nTitre: {title}\n\nDescription: {description}\n"
            
            return result
        except Exception as e:
            return f"Error fetching Jira issue {issue_key}: {str(e)}"
