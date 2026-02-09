import os
import base64
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import google.generativeai as genai

class VisionResourceInput(BaseModel):
    """Input for VisionResourceTool."""
    image_path: str = Field(..., description="Le chemin local vers l'image à analyser (ex: 'docs/resources/SCRUM-189/mockup.png').")
    query: str = Field(..., description="La question spécifique ou le contexte d'analyse pour l'image.")

class VisionResourceTool(BaseTool):
    name: str = "analyze_resource_image"
    description: str = (
        "OUTIL DE VISION PRIORITAIRE. À utiliser pour analyser les maquettes, screenshots ou schémas "
        "présents dans 'docs/resources/'. Permet d'extraire des détails visuels invisibles dans le texte Jira."
    )
    args_schema: Type[BaseModel] = VisionResourceInput

    def _run(self, image_path: str, query: str) -> str:
        # Tenter de trouver l'image à la racine ou dans le dossier automation/
        actual_path = image_path
        if not os.path.exists(actual_path):
            actual_path = os.path.join("automation", image_path)
        
        if not os.path.exists(actual_path):
            return f"Erreur : Le fichier image {image_path} est introuvable (tenté aussi {actual_path})."

        try:
            # Initialisation de l'API Google Generative AI (Vision)
            # On réutilise la clé API du système
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                return "Erreur : GOOGLE_API_KEY non configurée."
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-flash-latest')

            # Lecture et encodage de l'image
            with open(actual_path, "rb") as image_file:
                image_data = image_file.read()
                
            contents = [
                query,
                {
                    "mime_type": "image/png" if image_path.endswith(".png") else "image/jpeg",
                    "data": image_data
                }
            ]

            response = model.generate_content(contents)
            return response.text

        except Exception as e:
            return f"Erreur lors de l'analyse de l'image : {str(e)}"
