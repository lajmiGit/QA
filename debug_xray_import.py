
import os
import sys
from dotenv import load_dotenv

# Ensure the src module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.tools.xray_tool import XrayImportTool

# Load environment variables
load_dotenv()

def debug_xray():
    print("--- Debugging XrayImportTool ---")
    
    # Check env vars
    client_id = os.getenv("XRAY_CLIENT_ID")
    client_secret = os.getenv("XRAY_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("ERROR: XRAY_CLIENT_ID or XRAY_CLIENT_SECRET missing in .env")
        return

    print(f"Client ID present: {bool(client_id)}")
    
    # Sample Gherkin (Reconstructed from logs)
    gherkin_content = """
Feature: Add Product to Basket from Homepage

  As a shopper
  I want to be able to add products to my basket directly from the homepage
  So that I can quickly select items I want to buy without navigating to details

  Scenario: Add available product to basket
    Given I am on the homepage
    And the product "Apple Juice" has stock greater than 0
    When I click the "Add to Basket" button for "Apple Juice"
    Then the basket badge should show "1"
    """
    
    tool = XrayImportTool()
    
    # Test with project key 'SCRUM' as used in the failure
    print("\nAttempting import with project_key='SCRUM'...")
    try:
        result = tool._run(gherkin_content=gherkin_content, project_key="SCRUM")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_xray()
