import json
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class QueryKnowledgeInput(BaseModel):
    """Input for QueryKnowledgeTool."""
    question: str = Field(..., description="La question en langage naturel à poser à la mémoire du projet (ex: 'Quelles sont les règles de login validées ?').")

class QueryKnowledgeTool(BaseTool):
    name: str = "query_knowledge"
    description: str = "Interroger le 'Cerveau du Projet' (Mémoire Sémantique) pour obtenir des réponses basées sur l'historique, les décisions passées et les règles validées."
    args_schema: Type[BaseModel] = QueryKnowledgeInput

    def _run(self, question: str) -> str:
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

        # Configuration de l'IA pour la lecture sémantique
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Erreur : GOOGLE_API_KEY non trouvée pour l'interrogation sémantique."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""
        Tu es le 'Cerveau du Projet', une mémoire vivante et interactive pour une équipe QA. 
        Ton rôle est de répondre de manière précise à la question d'un agent en te basant sur le document de référence ci-dessous.
        
        CONTENU DE LA MÉMOIRE DU PROJET (Project Brain) :
        ---
        {content}
        ---
        
        QUESTION DE L'AGENT :
        "{question}"
        
        INSTRUCTIONS :
        1. Sois factuel et cite scrupuleusement les règles ou décisions présentes dans la mémoire.
        2. Si la question porte sur un élément manquant, indique-le clairement mais essaie de fournir le contexte le plus proche.
        3. Ne réinvente pas de règles ; tu es le gardien de ce qui a été validé.
        4. Si tu lis de l'ancien JSON, traduis-le mentalement en informations structurées pour ta réponse.
        
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
        brain_path = "project_brain.md"
        
        current_brain = ""
        if os.path.exists(brain_path):
            with open(brain_path, 'r', encoding='utf-8') as f:
                current_brain = f.read()
        
        # Configuration de l'IA pour la rédaction/synthèse de mémoire
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return "Erreur : GOOGLE_API_KEY non trouvée pour la mise à jour sémantique."
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
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
