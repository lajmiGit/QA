
import os
import sys
import json
from src.tools.playwright_mcp import InspectPageTool, ListFilesTool
from dotenv import load_dotenv

load_dotenv()

def verify_tools():
    print("--- Verifying Enhanced MCP Tools (Local) ---")
    
    inspect_tool = InspectPageTool()
    list_tool = ListFilesTool()
    
    # 1. Test ListFiles with Metadata
    print("\n1. Testing ListFiles on 'resources/'...")
    try:
        # The tool result is a string representation of the MCP response
        files_json = list_tool._run(directory="resources")
        # Extract the JSON array from the 'text' field (it's often wrapped in 'content: [...]')
        import re
        match = re.search(r"text='(.*?)'", files_json, re.DOTALL)
        if match:
            raw_json = match.group(1).replace("\\n", "\n").replace("\\\"", "\"")
            files = json.loads(raw_json)
            for f in files[:5]:
                print(f"- {f.get('name')} | mtime: {f.get('mtime')} | size: {f.get('size')}")
        else:
            print(f"Could not parse output: {files_json}")
    except Exception as e:
        print(f"Error listing files: {str(e)}")

    # 2. Test InspectPage
    file_path = os.path.abspath("test_verification.html")
    target_url = f"file://{file_path}"
    print(f"\n2. Inspecting {target_url}...")
    
    try:
        result = inspect_tool._run(url=target_url)
        import re
        match = re.search(r"text='(.*?)'", result, re.DOTALL)
        if match:
            raw_json = match.group(1).replace("\\n", "\n").replace("\\\"", "\"")
            data = json.loads(raw_json)
            print(f"\nFound {len(data)} interactive elements.")
            print("-" * 50)
            for item in data:
                print(f"[{item.get('role').upper()}] {item.get('name')}")
                if item.get('suggestedLocator'):
                    print(f"  > Playwright: {item.get('suggestedLocator')}")
                print("-" * 20)
        else:
            print(f"Could not parse output: {result}")
                
    except Exception as e:
        print(f"Error during verification: {str(e)}")

if __name__ == "__main__":
    verify_tools()
