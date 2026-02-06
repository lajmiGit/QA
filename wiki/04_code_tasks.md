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

### 2. La Tâche d'Analyse (`analysis_task`)

```python
def analysis_task(self, agent, user_story_context=None, direct_input=None):
    ...
```
*   **Flexibilité** : Cette tâche peut maintenant prendre soit un `user_story_context` (venant de Jira), soit un `direct_input` (texte fourni manuellement).
*   **Prompting** : Elle transforme la donnée brute en un document d'analyse structuré (Règles, Critères, APIs).

### 2. La Tâche de Design (`test_design_task`)

```python
    def test_design_task(self, agent, analysis_context):
        return Task(
            description=...,
            agent=agent,
            context=[analysis_context], # <--- LE LIEN MAGIQUE
            expected_output="..."
        )
```
*   **Le Chaînage (`context`)** : Remarquez `context=[analysis_context]`.
    *   `analysis_context` sera l'objet `Task` de l'étape précédente.
    *   CrewAI va automatiquement prendre le résultat textuel de l'analyse et l'injecter dans le prompt de cette tâche de design.
    *   L'agent Designer n'a donc pas besoin de lire la User Story originale, il travaille sur l'analyse "digérée" par l'Analyste.

### 3. La Tâche de Code (`code_generation_task`)

```python
    def code_generation_task(self, agent, design_context):
        return Task(
            description=dedent(f"""
                Générer le code d'automatisation Playwright...
                Exigences Techniques:
                1. Utiliser le pattern Page Object Model (POM).
                ...
            """),
            ...
        )
```
*   **Spécificité Technique** : Ici, le prompt devient très technique. On demande du TypeScript et une structure de fichiers spécifique.
*   **Output Attendu** : On précise "Code complet, importable". Cela évite que le modèle ne réponde avec du pseudo-code ou des explications textuelles inutiles ("Voici le code..."). On veut directement la matière première.

### 5. La Revue (`review_task`)

C'est la dernière barrière de qualité. Elle prend le code généré en contexte et demande au Superviseur de le valider techniquement et fonctionnellement.

### 6. L'Import Xray (`xray_push_task`)

```python
def xray_push_task(self, agent, review_context, design_context):
    ...
    expected_output="Une confirmation de l'import réussi dans Xray..."
```
*   **Action Finale** : Cette tâche prend les scénarios validés et les pousse vers Xray via l'outil dédié. Elle ferme la boucle de l'automatisation.
