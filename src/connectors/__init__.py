from .jira import JiraConnector
from .text import TextConnector

def get_connector(source_type: str):
    connectors = {
        "jira": JiraConnector(),
        "text": TextConnector(),
        # AzureConnector() peut être ajouté ici plus tard
    }
    return connectors.get(source_type.lower(), TextConnector())
