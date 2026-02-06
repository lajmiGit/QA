
import os
import sys
from dotenv import load_dotenv

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from src.tools.xray_tool import XrayImportTool

load_dotenv()

def debug_background_import():
    print("--- Debugging Xray Background Import ---")
    tool = XrayImportTool()
    project_key = "SCRUM"

    # CASE 1: With Background
    gherkin_bg = """
Feature: Debug Background

  Background:
    Given a preconditions exists

  Scenario: Scene with Background
    Given I act
    Then I succeed
"""
    print(f"\n[TEST 1] Importing Gherkin WITH Background...")
    try:
        res_bg = tool._run(gherkin_content=gherkin_bg, project_key=project_key)
        print(f"Result: {res_bg}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

    # CASE 2: Without Background
    gherkin_simple = """
Feature: Debug No Background

  Scenario: Scene Simple
    Given I act simply
    Then I succeed simply
"""
    print(f"\n[TEST 2] Importing Gherkin WITHOUT Background...")
    try:
        res_simple = tool._run(gherkin_content=gherkin_simple, project_key=project_key)
        print(f"Result: {res_simple}")
    except Exception as e:
        print(f"EXCEPTION: {e}")

if __name__ == "__main__":
    debug_background_import()
