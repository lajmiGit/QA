from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

class HumanInputSchema(BaseModel):
    """Input schema for HumanInputTool."""
    question: str = Field(..., description="La question à poser à l'utilisateur pour obtenir une clarification.")

class HumanInputTool(BaseTool):
    name: str = "ask_human"
    description: str = (
        "Utilisez cet outil pour poser une question à l'utilisateur lorsque vous avez un doute "
        "sur un sélecteur CSS, une URL de redirection ou toute information technique ambigüe. "
        "Cela évite de générer du code arbitraire ou erroné."
    )
    args_schema: Type[BaseModel] = HumanInputSchema

    def _run(self, question: str) -> str:
        # S'assurer d'écrire sur le vrai terminal pour la visibilité
        print(f"\n\n{'='*60}")
        print(f"📢 [INTERVIEWER EXPERT] : {question}")
        print(f"{'='*60}")
        print("\n👇 ATTENTE DE VOTRE RÉPONSE CI-DESSOUS.")
        print("👉 Veuillez saisir votre texte et appuyer sur ENTREE pour continuer.")
        
        try:
            user_response = input("\nVotre réponse > ")
            if not user_response.strip():
                return "L'utilisateur n'a rien répondu. Veuillez insister poliment."
            return user_response
        except EOFError:
            return "ERREUR : Stdin non interactif. Lancez le script dans un VRAI terminal (Terminal Mac/Zsh)."
        except Exception as e:
            return f"ERREUR technique : {str(e)}"
