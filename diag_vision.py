import os
import sys
from src.tools.playwright_mcp import ListFilesTool
from src.tools.vision_tool import VisionResourceTool
from dotenv import load_dotenv

load_dotenv()

def diagnostic():
    print("--- Diagnostic des Outils de Vision ---")
    
    # 1. Test ListFiles
    print("\n1. Test de ListFiles sur 'docs/resources/'...")
    list_tool = ListFilesTool()
    try:
        files = list_tool._run(directory="docs/resources")
        print(f"Résultat ListFiles: {files}")
    except Exception as e:
        print(f"Erreur ListFiles: {str(e)}")
        
    # 2. Test Vision avec une image réelle
    print("\n2. Test de VisionResourceTool...")
    vision_tool = VisionResourceTool()
    # On prend la première image trouvée
    image_path = "docs/resources/SCRUM-189/mockup1.png"
    print(f"Tentative d'analyse de : {image_path}")
    try:
        result = vision_tool._run(image_path=image_path, query="Qu'est-ce que tu vois sur cette image ?")
        print(f"Résultat Vision: {result[:200]}...")
    except Exception as e:
        print(f"Erreur Vision: {str(e)}")

if __name__ == "__main__":
    diagnostic()
