# Explication du Code : `src/agents.py`

Ce fichier définit les "cerveaux" de notre système. Nous utilisons la classe `Agent` de la librairie **CrewAI**.

## Concepts Clés de CrewAI

Un Agent dans CrewAI est défini par trois attributs principaux qui orientent comportement du LLM (Large Language Model) :

1.  **Role** : Le titre du poste. Cela dit au LLM "qui il est".
2.  **Goal** : L'objectif précis. Cela dit au LLM "ce qu'il doit accomplir".
3.  **Backstory** : Le contexte et la personnalité. Cela donne de la profondeur et des directives implicites sur le style et la qualité attendue.

## Analyse du Code Ligne par Ligne

### 1. Configuration et Imports

```python
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

load_dotenv() # Charge les variables du fichier .env (ex: GOOGLE_API_KEY)
```

Ici, nous importons `ChatGoogleGenerativeAI`. C'est le connecteur qui permet à CrewAI de parler avec Google Gemini.
`load_dotenv()` est crucial : il va chercher votre clé API sans qu'on ait besoin de l'écrire en dur dans le code (sécurité).

### 2. Initialisation du LLM (Stratégie Hybride) [OPTIMISÉ]

Nous utilisons désormais une stratégie hybride pour équilibrer puissance de raisonnement et rapidité/coût.

```python
# Configuration LLM PRO (Raisonnement complexe)
self.llm_pro = LLM(
    model=f"google/{MODEL_PRO}",
    api_key=os.getenv("GOOGLE_API_KEY"),
    max_rpm=MAX_RPM_PRO
)

# Configuration LLM FLASH (Exploration et Tâches simples)
self.llm_flash = LLM(
    model=f"google/{MODEL_FLASH}",
    api_key=os.getenv("GOOGLE_API_KEY"),
    max_rpm=MAX_RPM_FLASH
)
```

*   **Gemini Pro (`MODEL_PRO`)** : Réservé aux tâches critiques nécessitant une logique fine (Designer, SDET, Superviseur).
*   **Gemini Flash (`MODEL_FLASH`)** : Utilisé pour les tâches à haut volume ou exploratoires (Analyste, Dialogue, Intégration).
*   **`max_rpm`** : Contrôle strict du débit pour éviter les erreurs `429 (Quota Exceeded)`.

### 3. La Classe `LaboQaAgents`

#### L'Analyste (Requirement Specialist) [OPTIMISÉ]

```python
def analyst_agent(self):
    return Agent(
        role='Analyste QA (Requirement Specialist)',
        ...
        llm=self.llm_flash,
        tools=[self.query_tool, VisionResourceTool(), VideoResourceTool(), ListFilesTool(), HumanInputTool()]
    )
```

*   **Discovery Visuelle Ciblée [NEW]** : L'agent possède désormais l'outil `HumanInputTool` (via `ask_human`). 
*   **Protocole Interactif** : Au lieu de scanner tout le dossier `resources/`, il demande à l'utilisateur de choisir un sous-dossier spécifique (ex: `resources/SCRUM-326`). Cela réduit drastiquement la consommation de tokens Vision.

#### Les Interviewers (Specialized Validation Agents)

1.  **Requirement Interviewer** : Expert en Analyse de Besoins. Valide les règles point par point.
2.  **Design Interviewer** : Validateur de Design & JDD. Applique la **Boucle de Sécurité** pour le "GO" final.

#### Le Designer (BDD Specialist)
*   **LLM** : Utilise le modèle **Pro** pour garantir des scénarios Gherkin complexes et sans fautes de syntaxe.

#### Le SDET (Automation Agent)
*   **Diagnostic Visuel Assisté par IA** : Utilise `analyze_resource_image` et `explore_page_with_actions` pour confronter le code au rendu réel.
*   **LLM** : Utilise le modèle **Pro** pour la génération de code TypeScript robuste.

#### Le Superviseur (QA Lead)
*   **Delegation** : Seul agent avec `allow_delegation=True`, lui permettant de retourner une tâche à un agent si la qualité n'est pas au rendez-vous.

#### L'Agent d'Intégration (Jira/Xray Connector)
*   **LLM** : Utilise **Flash** car le parsing JSON des APIs ne nécessite pas de raisonnement complexe.
