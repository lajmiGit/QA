import os
import time
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import google.generativeai as genai
from src.config import MODEL_FLASH
from src.utils.resiliency import retry_gemini_api
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Modèle optimisé pour la vidéo (Configuré via main.py)
video_model = genai.GenerativeModel(MODEL_FLASH)

class VideoResourceInput(BaseModel):
    """Input for VideoResourceTool."""
    video_path: str = Field(..., description="Le chemin local vers la vidéo à analyser (ex: 'resources/SCRUM-189/recording.mp4' ou 'test-results/.../video.webm').")
    query: str = Field(..., description="La question spécifique ou le contexte d'analyse pour la vidéo (ex: 'Décris l'enchaînement des étapes' ou 'Pourquoi le test a échoué ?').")

class VideoResourceTool(BaseTool):
    name: str = "analyze_scenario_video"
    description: str = (
        "OUTIL DE COMPRÉHENSION VIDÉO. À utiliser pour analyser des enregistrements de scénarios, "
        "des bugs filmés ou des démos. Permet de comprendre la dimension temporelle et les interactions fluides."
    )
    args_schema: Type[BaseModel] = VideoResourceInput

    def _run(self, video_path: str, query: str) -> str:
        # Priorité de recherche : Dossier resources/ racine, puis direct, puis automation/
        paths_to_check = [
            os.path.join("resources", video_path),
            video_path,
            os.path.join("automation", video_path)
        ]
        
        actual_path = None
        for p in paths_to_check:
            if os.path.exists(p):
                actual_path = p
                break
        
        if not actual_path:
            return f"Erreur : Le fichier vidéo {video_path} est introuvable (vérifié dans resources/, racine et automation/)."

        try:
            # Upload du fichier via la File API de Google
            print(f"[VIDEO TOOL] Uploading {actual_path}...")
            video_file = genai.upload_file(path=actual_path)
            
            # Attente que la vidéo soit prête (processing côté Google)
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = genai.get_file(video_file.name)

            if video_file.state.name == "FAILED":
                return "Erreur : Le traitement de la vidéo par l'IA a échoué."

            # Analyse avec Gemini 1.5 Flash
            print(f"[VIDEO TOOL] Analyzing video with query: {query}")
            response = video_model.generate_content([video_file, query])
            
            # Nettoyage optionnel : on pourrait supprimer le fichier après usage, 
            # mais Google le fait automatiquement après 2 jours.
            
            return response.text

        except Exception as e:
            return f"Erreur lors de l'analyse vidéo : {str(e)}"
