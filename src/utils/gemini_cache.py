import os
import datetime
import google.generativeai as genai
from google.generativeai import caching
from src.config import MODEL_PRO, MODEL_FLASH
from dotenv import load_dotenv

load_dotenv()

class GeminiContextManager:
    """
    Gère le cycle de vie des caches Gemini pour centraliser la connaissance du projet.
    Supporte plusieurs modèles (Pro et Flash) en parallèle.
    """
    def __init__(self):
        self.caches = {} # { "models/gemini-1.5-pro...": "cache_id" }
        self.display_name_prefix = "labo_qa_global_memory"

    def initialize_all_caches(self):
        """
        Initialise les caches pour les modèles Pro et Flash.
        """
        print("🧹 Nettoyage des anciens caches Gemini...")
        try:
            for c in caching.CachedContent.list():
                if c.display_name.startswith(self.display_name_prefix):
                    print(f"  - Suppression : {c.name} ({c.display_name})")
                    c.delete()
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage : {str(e)}")

        # Création des caches pour les deux modèles
        self._create_cache_for_model(MODEL_PRO)
        self._create_cache_for_model(MODEL_FLASH)

    def _create_cache_for_model(self, model_short_name, wiki_dir="wiki"):
        """
        Crée un cache spécifique pour un modèle donné.
        Note: Le chargement du Wiki a été désactivé pour alléger le contexte (Lean Context).
        """
        model_full_name = f"models/{model_short_name}"
        display_name = f"{self.display_name_prefix}_{model_short_name}"
        
        print(f"🚀 Initialisation du cache pour {model_full_name} (Mode Lean)...")
        
        # Wiki désactivé
        contents = []
        
        # Si on voulait remettre le Wiki, c'était ici.
        # Pour l'instant on garde une liste vide pour initialiser un cache minimal.

        if not contents:
            print(f"⚠️ Aucun contenu à cacher pour {model_short_name}. Création du cache annulée.")
            return None

        try:
            ttl_delta = datetime.timedelta(hours=1)
            project_cache = caching.CachedContent.create(
                model=model_full_name,
                display_name=display_name,
                system_instruction=(
                    "Tu es l'Expert Technique du Labo QA IA. "
                    "Tu utilises ton intelligence et les informations fournies dynamiquement pour répondre."
                ),
                contents=contents,
                ttl=ttl_delta,
            )
            self.caches[model_full_name] = project_cache.name
            print(f"✅ Cache créé pour {model_short_name} : {project_cache.name}")
            return project_cache.name
        except Exception as e:
            print(f"❌ Erreur création cache pour {model_short_name} : {str(e)}")
            return None

    def cleanup(self):
        """
        Supprime tous les caches gérés.
        """
        print("🧹 Nettoyage final des caches Gemini...")
        for model, cache_id in self.caches.items():
            try:
                cache = caching.CachedContent.get(cache_id)
                cache.delete()
                print(f"✨ Cache {cache_id} supprimé.")
            except Exception as e:
                print(f"⚠️ Erreur nettoyage cache {cache_id} : {str(e)}")
        self.caches = {}

    def get_cache_id_for_model(self, model_name):
        """
        Récupère l'ID du cache pour un modèle spécifique.
        Gère les formats 'models/...' et '...-preview'
        """
        if not model_name.startswith("models/"):
            model_name = f"models/{model_name}"
        return self.caches.get(model_name)

# Instance globale
context_manager = GeminiContextManager()
