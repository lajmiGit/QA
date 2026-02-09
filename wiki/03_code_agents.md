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

### 2. Initialisation du LLM (Le Cerveau)

```python
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    verbose=True,
    temperature=0.2,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)
```

*   **`model="gemini-1.5-flash"`** : Nous utilisons la version "Flash" car elle est rapide et efficace pour des tâches logiques.
*   **`temperature=0.2`** : Très important !
    *   Une température proche de 0 (0.2) rend le modèle **déterministe** et **précis**.
    *   Une température proche de 1 (0.8) rend le modèle **créatif** et **aléatoire**.
    *   Pour du code et de la QA, on veut de la précision, donc 0.2 est idéal.

### 3. La Classe `LaboQaAgents`

Nous avons regroupé nos agents dans une classe pour pouvoir les instancier facilement.

#### L'Analyste (Requirement Agent)

```python
def analyst_agent(self):
    return Agent(
        role='Analyste QA (Requirement Agent)',
        goal='Décortiquer les User Stories...',
        ...
    )
```

#### Les Interviewers (Specialized Validation Agents) [NEW]

Nous avons introduit deux agents spécialisés pour la validation interactive :

1.  **Requirement Interviewer** : 
    - **Rôle** : Expert en Analyse de Besoins.
    - **Mission** : Valider les règles de gestion point par point avec l'utilisateur.
    - **Outils** : `ask_human`, `query_knowledge`, `update_knowledge`.
2.  **Design Interviewer** :
    - **Rôle** : Validateur de Design & JDD.
    - **Mission** : Valider les scénarios Gherkin et les Examples. Applique la **Boucle de Sécurité** pour le "GO" final.
    - **Outils** : `ask_human`, `query_knowledge`, `update_knowledge`.

> [!IMPORTANT]
> Ces agents sont les seuls à interagir directement avec l'utilisateur via le terminal.

#### Le Designer (BDD Specialist)

```python
def designer_agent(self):
    return Agent(
        role='Designer de Tests (BDD Specialist)',
        ...
        backstory="""Vous êtes un spécialiste du BDD..."""
    )
```
*   **Spécificité** : Son rôle est centré sur le **Gherkin**. Le backstory mentionne explicitement "Given/When/Then" et "lisible par le métier". Cela force le modèle à produire ce format strict.

#### Le SDET (Automation Agent)

```python
def sdet_agent(self):
    return Agent(
        role='Ingénieur SDET (Automation Agent)',
        ...
        backstory="""...Vous suivez strictement le pattern Page Object Model..."""
    )
```
*   **SDET (Software Development Engineer in Test)** : C'est un développeur logiciel qui est spécialisé dans le test. Contrairement à un testeur manuel, il écrit du code pour tester le code.
*   **Point Critique** : Le prompt insiste sur le **Page Object Model (POM)**. Sans cette instruction dans le backstory, le modèle pourrait générer des scripts simples et "sales" (tout dans un seul fichier). Ici, on lui impose une architecture logicielle propre dès sa définition.

#### Le SDET Interactif (State-Aware) [NEW]

Depuis la mise à jour "Interactive Mode", cet agent dispose d'une capacité unique : **la Génération de Code Consciente de l'État (State-Aware Code Generation)**.

*   **Problème** : Comment écrire le Page Object d'une page accessible *seulement après login* (ex: Dashboard) sans deviner les sélecteurs ?
*   **Solution** : L'outil `explore_page_with_actions`.
*   **Fonctionnement** :
    1.  L'agent reçoit l'ordre de coder la page Dashboard.
    2.  Il utilise l'outil pour **exécuter réellement** le login (naviguer vers `/login`, remplir user/pass, cliquer).
    3.  L'outil lui renvoie le **DOM réel** de la page d'arrivée.
    4.  L'agent génère alors les sélecteurs parfaits basés sur la réalité, pas sur des suppositions.

#### Le Superviseur (QA Lead)

```python
def supervisor_agent(self):
    return Agent(
        role='Superviseur (QA Lead)',
        goal='Assurer la qualité globale des livrables...',
        backstory="""Vous êtes le Lead QA. Vous avez l'œil pour les détails...""",
        verbose=True,
        allow_delegation=True, # Notez la différence ici !
        llm=self.llm
    )
```
*   **Delegation** : C'est le seul agent avec `allow_delegation=True`. Cela signifie que s'il trouve le travail mal fait, il peut demander à un autre agent (ex: le SDET ou le Designer) de corriger sa copie.

#### L'Agent d'Intégration (Jira/Xray Connector)

```python
def integration_agent(self):
    return Agent(
        role='Agent d\'Intégration (Jira/Xray Connector)',
        goal='Gérer toutes les interactions avec Jira et Xray.',
        backstory="""Vous êtes responsable de la communication avec les outils externes...""",
        verbose=True,
        allow_delegation=False,
        llm=self.llm,
        tools=[JiraIssueTool(), XrayImportTool()]
    )
```
*   **Centralisation** : Cet agent est le seul à posséder les `tools` externes. Cela permet de séparer la logique de métier (Analyse, Design, Code) de la logique technique d'API (Jira, Xray).
