# Explication du Code : `src/tasks.py`

Ce fichier définit le "Travail" à effectuer. Si les Agents sont les employés, les Tâches (`Task`) sont les ordres de mission.

## Concepts Clés de CrewAI (Tâches)

Une `Task` lie trois choses :
1.  **Quoi faire** (`description`) : L'instruction précise.
2.  **Qui le fait** (`agent`) : L'employé responsable.
3.  **Ce qu'on attend** (`expected_output`) : La définition du "Done".

Un quatrième concept crucial est le **Contexte** (`context`). C'est ce qui permet de chaîner les tâches : la sortie de la tâche A devient l'entrée de la tâche B.

## Analyse du Code

### 1. La Tâche de Récupération (`jira_fetch_task`)

```python
def jira_fetch_task(self, agent, issue_key):
    return Task(
        description=...,
        agent=agent,
        expected_output="Le contenu brut de la User Story récupéré depuis Jira."
    )
```
*   **Rôle** : Cette tâche est optionnelle. Elle n'est lancée que si un ID Jira est fourni. Elle permet d'alimenter la suite du pipeline avec du contenu réel.

### 2. La Tâche d'Analyse (`analysis_task`) [BOOSTÉE]

```python
def analysis_task(self, agent, user_story_context=None, direct_input=None):
    ...
```

*   **Discovery Visuelle Ciblée [NEW]** : 
    - **Étape 1 : Liste** : Listing de `resources/` pour identifier les tickets disponibles.
    - **Étape 2 : Dialogue** : Demande à l'utilisateur quel dossier analyser via `ask_human`.
    - **Étape 3 : Delta** : Analyse uniquement les fichiers nouveaux ou modifiés dans le dossier choisi.
*   **Context Trimming [NEW]** : Utilisation de `output_pydantic=RuleInventory` pour garantir une sortie structurée et minimiser la taille du contexte transmis aux tâches suivantes.

### 3. Les Tâches de Validation (Interview Tasks)

#### `interview_analysis_task`
- **Agent** : `RequirementInterviewer`
- **Livrable** : `RuleInventory` (Pydantic) mis à jour après validation humaine.

#### `interview_design_task`
- **Agent** : `DesignInterviewer`
- **Livrable** : `GherkinDesign` (Pydantic) incluant les scénarios validés et le "GO" final.

### 4. La Tâche de Design (`test_design_task`)
*   **Output** : Utilise le modèle Pydantic `GherkinDesign`.

### 5. La Tâche de Code (`code_generation_task`) [BOOSTÉE]

```python
def code_generation_task(self, agent, design_context):
    ...
```

*   **Mode Interactif (State-Aware)** : L'agent utilise `explore_page_with_actions` pour "voir" les pages cachées.
*   **BOUCLE DE DEBUG : PROTOCOLE RE-INSPECT (STRICT)** : En cas d'échec du test, l'agent re-navigue, inspecte le DOM Aria et analyse visuellement l'erreur avant de corriger.
*   **Structured Output** : Utilise `output_pydantic=CodeGenerationOutput` pour produire les fichiers `.feature`, `.page.ts` et `.steps.ts` de manière propre.

### 6. La Revue (`review_task`)
*   **Supervision** : Validation technique du code généré.

### 7. L'Import Xray (`xray_push_task`)
*   **Action Finale** : Pousse les scénarios validés vers Xray Cloud, assurant la traçabilité complète entre la US et les tests automatisés.
