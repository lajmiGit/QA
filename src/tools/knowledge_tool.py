import json
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Any
import google.generativeai as genai
from src.config import MODEL_PRO, MODEL_FLASH
from src.utils.resiliency import retry_gemini_api
from src.utils.gemini_cache import context_manager # Import du manager de cache
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Note: genai est configuré globalement dans main.py (via load_dotenv)
if not os.getenv("GOOGLE_API_KEY"):
    print("WARNING: GOOGLE_API_KEY non trouvée dans l'environnement.")

class QueryKnowledgeInput(BaseModel):
    """Input for QueryKnowledgeTool."""
    question: str = Field(..., description="La question en langage naturel à poser à la mémoire du projet (ex: 'Quelles sont les règles de login validées ?').")

class QueryKnowledgeTool(BaseTool):
    name: str = "query_knowledge"
    description: str = "Interroger le 'Cerveau du Projet' (Mémoire Sémantique) pour obtenir des réponses basées sur l'historique, les décisions passées et les règles validées."
    args_schema: Type[BaseModel] = QueryKnowledgeInput

    def _run(self, question: str) -> str:
        # Utilisation d'un modèle léger pour la lecture
        model = genai.GenerativeModel(MODEL_FLASH)
        
        brain_path = "project_brain.md"
        json_path = "knowledge_base.json"
        
        # Acquisition du contenu (Priorité MD, fallback JSON)
        content = ""
        if os.path.exists(brain_path):
            with open(brain_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                content = "CONTENU JSON (ANCIENNE MÉMOIRE) :\n" + json.dumps(json.load(f), indent=2, ensure_ascii=False)
        else:
            return "La mémoire du projet est actuellement vide."

        cache_id = context_manager.get_cache_id_for_model(MODEL_FLASH)
        
        # CONSTRUCTION DU PROMPT HYBRIDE
        # 1. Le Brain (Dynamique) est toujours passé dans le prompt
        brain_prompt_part = f"""
        CONTENU DE LA MÉMOIRE VIVANTE (Project Brain) :
        ---
        {content}
        ---
        """
        
        if cache_id:
            # OPTIMISATION : Utilisation du cache serveur pour le Wiki
            print(f"💎 [HYBRID CACHE] Wiki via {cache_id} + Brain via Prompt")
            try:
                # Création d'un modèle lié au cache
                model_with_cache = genai.GenerativeModel.from_cached_content(cached_content=cache_id)
                response = model_with_cache.generate_content(
                    f"{brain_prompt_part}\n\nQUESTION AGENT : {question}"
                )
                return response.text
            except Exception as e:
                print(f"⚠️ Échec du cache {cache_id}, repli sur le mode standard : {str(e)}")
        
        # MODE STANDARD (Fallback complet si pas de cache)
        prompt = f"""
        {brain_prompt_part}
        
        QUESTION DE L'AGENT :
        "{question}"
        
        INSTRUCTIONS :
        1. Sois factuel. Utilise le Project Brain ci-dessus et tes connaissances du projet.
        2. Réponds précisément à la question.
        
        RÉPONSE DU CERVEAU :
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Erreur lors de l'interrogation du cerveau : {str(e)}"

class UpdateKnowledgeInput(BaseModel):
    """Input for UpdateKnowledgeTool."""
    update_type: str = Field(..., description="Le type d'information (ex: 'Règles US_001', 'Décision Technique', 'JDD Préférés').")
    content: Any = Field(..., description="Le contenu textuel ou la liste de points à mémoriser.")
    context: str = Field(..., description="Le contexte global (ex: 'SCRUM-272', 'Authentification').")

class UpdateKnowledgeTool(BaseTool):
    name: str = "update_knowledge"
    description: str = "Mettre à jour le 'Cerveau du Projet' en y intégrant de nouvelles informations de manière synthétique et structurée en Markdown."
    args_schema: Type[BaseModel] = UpdateKnowledgeInput

    def _run(self, update_type: str, content: Any, context: str) -> str:
        # Utilisation d'un modèle puissant pour la synthèse
        model = genai.GenerativeModel(MODEL_PRO)
        
        brain_path = "project_brain.md"
        
        current_brain = ""
        if os.path.exists(brain_path):
            with open(brain_path, 'r', encoding='utf-8') as f:
                current_brain = f.read()
        
        prompt = f"""
        Tu es l'Editeur du 'Cerveau du Projet'. Ta mission est de maintenir un document Markdown propre, structuré et synthétique qui sert de mémoire à long terme pour l'équipe QA.
        
        NOUVELLE INFORMATION À INTÉGRER :
        - Type : {update_type}
        - Contexte : {context}
        - Contenu : {json.dumps(content, indent=2, ensure_ascii=False) if not isinstance(content, str) else content}
        
        DOCUMENT ACTUEL (PROJECT BRAIN) :
        {current_brain if current_brain else "# Project Brain\nCe document contient l'historique et les connaissances du projet."}
        
        DIRECTIVES D'ÉCHELLE (STRICTES) :
        1. Organize le document par grandes sections (ex: # Règles Métier, # Architecture, # Jeux de Données).
        2. Intègre la nouvelle information dans la section appropriée.
        3. **SYNTHÈSE** : Ne te contente pas d'ajouter du texte en bas. Si l'information complète ou modifie un point existant, réécris la section pour qu'elle soit cohérente.
        4. Élimine les doublons.
        5. Utilise des tableaux Markdown pour les listes de règles ou de JDD si cela améliore la lisibilité.
        6. Garde les références aux IDs Jira (ex: [SCRUM-272]).
        
        RETOURNE UNIQUEMENT LE CONTENU INTÉGRAL DU NOUVEAU FICHIER MARKDOWN (Sans balises de code ```markdown).
        """
        
        try:
            response = model.generate_content(prompt)
            new_brain_content = response.text.strip()
            # Nettoyage profond des balises markdown si l'IA les a incluses par erreur
            if new_brain_content.startswith('```'):
                lines = new_brain_content.splitlines()
                if lines[0].startswith('```'): lines = lines[1:]
                if lines[-1].startswith('```'): lines = lines[:-1]
                new_brain_content = "\n".join(lines).strip()
            
            with open(brain_path, 'w', encoding='utf-8') as f:
                f.write(new_brain_content)
            
            return f"Le Cerveau du Projet a été mis à jour et synthétisé pour : {context}."
        except Exception as e:
            return f"Erreur lors de la mise à jour sémantique : {str(e)}"
