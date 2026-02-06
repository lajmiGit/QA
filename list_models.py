import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("Erreur : GOOGLE_API_KEY non trouvée dans le fichier .env")
else:
    client = genai.Client(api_key=api_key)
    print(f"--- Modèles disponibles pour cette clé ---")
    try:
        for model in client.models.list():
            # On essaye de trouver le nom ou l'ID
            name = getattr(model, 'name', 'N/A')
            display_name = getattr(model, 'display_name', 'N/A')
            print(f"- {name} ({display_name})")
    except Exception as e:
        print(f"Erreur lors de la récupération des modèles : {e}")
