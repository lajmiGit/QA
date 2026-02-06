# Explication du Code : `main.py`

C'est le chef d'orchestre. Ce fichier assemble les agents et les tâches pour former un "Crew" (Équipe) et lance le travail.

## Analyse du Déroulement

### 0. Système de Logging et Gestion de Quota

*   **Logging** : Le script inclut un `Logger` qui capture tout ce qui s'affiche dans le terminal vers `output/execution.log`.
*   **Gestion de Quota (Rate Limiting)** : Pour éviter l'erreur `429 Resource Exhausted` de l'API Google Gemini, un mécanisme de pause a été ajouté via un **callback de tâche**. Entre chaque étape du Crew, le système marque une pause de **10 secondes**.

### 1. Initialisation

```python
def run():
    # ...
    # 1. Instanciation des Agents
    agents = LaboQaAgents()
    analyst = agents.analyst_agent()
    designer = agents.designer_agent()
    sdet = agents.sdet_agent()
    supervisor = agents.supervisor_agent()
    integration = agents.integration_agent() # Nouvel agent !
```
On recrute maintenant **5 agents**. L'agent d'intégration est ajouté pour gérer les flux entrants (Jira) et sortants (Xray).

### 2. Définition de l'Entrée (Input)

```python
    # 2. Définition de la User Story
    us01_content = """..."""
```
Dans un vrai projet, cette User Story pourrait venir d'un fichier texte, de Jira, ou d'une entrée utilisateur. Pour l'instant, elle est codée en dur pour faciliter les tests.

### 3. Création et Chaînage des Tâches

Le pipeline est maintenant dynamique. Si une `--issue` est fournie :
1.  **`tsk_fetch`** : L'Intégrateur récupère le ticket.
2.  **`tsk_analysis`** : L'Analyste travaille sur le résultat de `tsk_fetch`.

Sinon, l'Analyste travaille sur une US codée en dur (`direct_input`).

Le reste du pipeline reste stable : `Design -> Code -> Revue`, suivi d'une étape finale :
3.  **`tsk_push`** : L'Intégrateur pousse le Gherkin validé dans Xray.

### 4. Le Crew (L'Équipe)

```python
    crew = Crew(
        agents=[analyst, designer, sdet, supervisor, integration],
        tasks=active_tasks,
        verbose=True,
        process=Process.sequential
    )
```
*   **`agents`** : Liste complète des 5 agents.
*   **`tasks=active_tasks`** : La liste des tâches est construite dynamiquement (avec ou sans l'étape Jira initiale).
*   **`process=Process.sequential`** : Indique que les tâches doivent être exécutées l'une après l'autre, dans l'ordre de la liste `tasks`.
*   **`verbose=True`** : Crucial pour comprendre ce qui se passe. Cela va afficher tout ce que les agents se disent et font dans le terminal.

### 5. Exécution

```python
    result = crew.kickoff()
```
Cette méthode lance tout le processus. Le script va "bloquer" ici pendant quelques minutes le temps que l'IA travaille. Une fois fini, le résultat final (la sortie de la dernière tâche, donc la revue du Superviseur) est stocké dans `result`.
