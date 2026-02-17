from .base import RequirementConnector
from atlassian import Jira
import os
from dotenv import load_dotenv

load_dotenv()

class JiraConnector(RequirementConnector):
    def fetch(self, issue_key: str) -> str:
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
            
            # Formater le résultat comme l'analyste l'attend
            result = f"--- JIRA ISSUE: {issue_key} ---\n"
            result += f"Project: {project_key}\n"
            result += f"Title: {title}\n"
            result += f"Description: {description}\n"
            
            return result
        except Exception as e:
            return f"Error connecting to Jira for {issue_key}: {str(e)}"
