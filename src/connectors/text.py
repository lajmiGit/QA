from .base import RequirementConnector
import os

class TextConnector(RequirementConnector):
    def fetch(self, content_or_path: str) -> str:
        # Si c'est un chemin de fichier existant, on le lit
        if os.path.exists(content_or_path):
            try:
                with open(content_or_path, 'r', encoding='utf-8') as f:
                    return f"--- TEXT SOURCE: {content_or_path} ---\n\n" + f.read()
            except Exception as e:
                return f"Error reading file {content_or_path}: {str(e)}"
        
        # Sinon on traite la chaîne comme le contenu direct
        return f"--- DIRECT INPUT ---\n\n{content_or_path}"
