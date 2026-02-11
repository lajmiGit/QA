import os
import base64
from typing import Type, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import google.generativeai as genai
from src.config import MODEL_FLASH
from src.utils.resiliency import retry_gemini_api
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Modèle vision (Configuré via main.py)
# On initialise le modèle vision une fois à l'import
vision_model = genai.GenerativeModel(MODEL_FLASH)

class VisionResourceInput(BaseModel):
    """Input for VisionResourceTool."""
    image_path: str = Field(..., description="Le chemin local vers l'image à analyser (ex: 'resources/SCRUM-189/mockup.png').")
    query: str = Field(..., description="La question spécifique ou le contexte d'analyse pour l'image.")

class VisionResourceTool(BaseTool):
    name: str = "analyze_resource_image"
    description: str = (
        "OUTIL DE VISION PRIORITAIRE. À utiliser pour analyser les maquettes, screenshots ou schémas "
        "présents dans 'resources/'. Permet d'extraire des détails visuels invisibles dans le texte Jira."
    )
    args_schema: Type[BaseModel] = VisionResourceInput

    def _run(self, image_path: str, query: str) -> str:
        # Priorité de recherche : Dossier resources/ racine, puis direct, puis automation/
        paths_to_check = [
            os.path.join("resources", image_path),
            image_path,
            os.path.join("automation", image_path)
        ]
        
        actual_path = None
        for p in paths_to_check:
            if os.path.exists(p):
                actual_path = p
                break
        
        if not actual_path:
            return f"Erreur : Le fichier image {image_path} est introuvable (vérifié dans resources/, racine et automation/)."

        try:
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

            response = vision_model.generate_content(contents)
            return response.text

        except Exception as e:
            return f"Erreur lors de l'analyse de l'image : {str(e)}"
