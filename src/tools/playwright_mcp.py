from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
from src.utils.mcp_client import McpClient
import os

# Global Client Instance (Singleton pattern for simplicity in this POC)
# In production, we might want to manage this lifecycle better.
_mcp_client = None

def get_mcp_client():
    global _mcp_client
    if _mcp_client is None:
        # Command to start the MCP server
        # We assume 'automation' is in the root and has 'package.json' with 'start:mcp'
        cmd = ["npm", "run", "start:mcp"]
        cwd = os.path.abspath("automation")
        _mcp_client = McpClient(cmd, cwd=cwd)
        if not _mcp_client.start():
            raise Exception("Failed to start MCP Server")
    return _mcp_client

# --- Output Models ---

class WriteFileInput(BaseModel):
    path: str = Field(..., description="Relative path to the file (e.g., 'tests/item.spec.ts')")
    content: str = Field(..., description="The full content to write.")

class ReadFileInput(BaseModel):
    path: str = Field(..., description="Relative path to the file to read.")

class RunTestInput(BaseModel):
    testFile: Optional[str] = Field(None, description="Optional. Specific test file to run. If omitted, runs all tests.")

# --- Tools ---

class WriteFileTool(BaseTool):
    name: str = "write_file"
    description: str = "Write content to a file in the automation project. Use this to create or update test files, page objects, or step definitions."
    args_schema: Type[BaseModel] = WriteFileInput

    def _run(self, path: str, content: str) -> str:
        client = get_mcp_client()
        result = client.call_tool("write_file", {"path": path, "content": content})
        # Result is likely a list of content objects from MCP
        return str(result)

class ReadFileTool(BaseTool):
    name: str = "read_file"
    description: str = "Read content from a file in the automation project."
    args_schema: Type[BaseModel] = ReadFileInput

    def _run(self, path: str) -> str:
        client = get_mcp_client()
        result = client.call_tool("read_file", {"path": path})
        return str(result)

class RunPlaywrightTestTool(BaseTool):
    name: str = "run_playwright_test"
    description: str = "Run Playwright tests. You can run all tests or target a specific file. Returns the test results."
    args_schema: Type[BaseModel] = RunTestInput

    def _run(self, testFile: Optional[str] = None) -> str:
        client = get_mcp_client()
        args = {}
        if testFile:
            args["testFile"] = testFile
        
        # This might take a while, so we need to ensure the client timeout is high
        result = client.call_tool("run_playwright_test", args)
        return str(result)

class ListFilesTool(BaseTool):
    name: str = "list_files"
    description: str = "List files in the automation directory to understand structure."
    
    
    def _run(self, directory: str = ".") -> str:
        client = get_mcp_client()
        result = client.call_tool("list_files", {"directory": directory})
        return str(result)

class InspectPageInput(BaseModel):
    url: str = Field(..., description="The URL to inspect (e.g. 'http://localhost:3000/login').")

class InspectPageTool(BaseTool):
    name: str = "inspect_page"
    description: str = "Visit a URL and return a summary of interactive elements (buttons, inputs) with their selectors. Use this BEFORE writing selectors."
    args_schema: Type[BaseModel] = InspectPageInput

    def _run(self, url: str) -> str:
        client = get_mcp_client()
        result = client.call_tool("inspect_page", {"url": url})
        return str(result)

class ScreenshotInput(BaseModel):
    url: str = Field(..., description="The URL to visit.")
    path: Optional[str] = Field("screenshot.png", description="Path to save the screenshot.")

class TakeScreenshotTool(BaseTool):
    name: str = "take_screenshot"
    description: str = "Take a screenshot of a page. Useful for debugging UI issues."
    args_schema: Type[BaseModel] = ScreenshotInput

    def _run(self, url: str, path: str = "screenshot.png") -> str:
        client = get_mcp_client()
        result = client.call_tool("take_screenshot", {"url": url, "path": path})
        return str(result)

class LogsInput(BaseModel):
    url: str = Field(..., description="The URL to visit.")

class GetConsoleLogsTool(BaseTool):
    name: str = "get_console_logs"
    description: str = "Get console logs and errors from a page. Useful for debugging JS crashes."
    args_schema: Type[BaseModel] = LogsInput

    def _run(self, url: str) -> str:
        client = get_mcp_client()
        result = client.call_tool("get_console_logs", {"url": url})
        return str(result)

class ExplorePageInput(BaseModel):
    url: str = Field(..., description="The start URL.")
    actions: list[dict] = Field(..., description="List of actions: [{'type': 'fill'|'click'|'wait', 'selector': '...', 'value': '...'}]")

class ExplorePageTool(BaseTool):
    name: str = "explore_page_with_actions"
    description: str = "Navigate and interact with a page to inspect its state (DOM). Use this to see pages behind login."
    args_schema: Type[BaseModel] = ExplorePageInput

    def _run(self, url: str, actions: list[dict]) -> str:
        client = get_mcp_client()
        result = client.call_tool("explore_page_with_actions", {"url": url, "actions": actions})
        return str(result)
