# Intégrations Jira & Xray

Le Labo QA IA utilise un **Agent d'Intégration** dédié pour centraliser toutes les communications avec l'écosystème Atlassian. Cela garantit une séparation claire entre l'intelligence de test et la connectivité technique.

## 1. Connecteur Jira (`JiraIssueTool`)

L'**Agent d'Intégration** utilise ce connecteur au tout début du cycle pour extraire dynamiquement les informations d'un ticket Jira.

### Fonctionnement :
- **Entrée** : Une clé de ticket Jira (ex: `QA-123`).
- **Action** : L'outil appelle l'API REST de Jira Cloud pour récupérer le **Projet**, le Résumé (Summary) et la Description de la US via la tâche `jira_fetch_task`.
- **Mémoire & JDD** : Les Interviewers couplent ces données avec la `knowledge_base.json` pour proposer des jeux de données historiques dès la récupération du ticket.
- **Transmission** : Le contenu récupéré (incluant le `Project Key`) est ensuite passé en contexte à l'**Analyste QA** et aux **Interviewers**.

### Utilisation :
Lancez le script avec l'argument `--issue` et `--project` (pour le projet cible Xray) :
```bash
python3 main.py --issue SCRUM-8 --project SCRUM
```

## 2. Connecteur Xray (`XrayImportTool`)

L'**Agent d'Intégration** intervient à nouveau à la toute fin du processus pour sauvegarder les scénarios finalisés dans Xray.

### Fonctionnement :
- **Action** : Une fois que le code et le Gherkin sont validés par le **Superviseur**, l'Agent d'Intégration lance la tâche `xray_push_task`.
- **Résultat** : Les scénarios Gherkin sont importés via l'endpoint `/import/feature`.
- **Stratégie Avancée** :
    1.  **Test Set** : Un Test Set portant le nom de la Feature (ex: `Modify Basket Item Quantity`) est créé ou réutilisé. Tous les tests créés y sont liés.
    2.  **Pre-Condition** : Si le Gherkin contient un `Background`, une Pre-Condition Xray est créée et liée aux tests correspondants.
    3.  **Output** : L'outil retourne les clés des Test Sets et Pre-Conditions créés pour une traçabilité complète.

## Configuration Requise (.env)

Assurez-vous d'avoir configuré les variables suivantes pour activer ces fonctionnalités :

```ini
# Jira
JIRA_URL=https://votre-instance.atlassian.net
JIRA_USER_EMAIL=votre-email@atlassian.com
JIRA_API_TOKEN=votre_token

# Xray Cloud
XRAY_CLIENT_ID=votre_client_id
XRAY_CLIENT_SECRET=votre_client_secret
```

> [!TIP]
> Si les variables Jira/Xray ne sont pas renseignées dans le `.env`, les agents utiliseront les valeurs par défaut (US01 Juice Shop) et ne tenteront pas l'export Xray.
