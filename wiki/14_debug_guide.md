# Guide de Diagnostic et Debug

Ce guide répertorie les outils et procédures pour diagnostiquer les problèmes de connectivité, de vision ou d'intégration au sein du framework.

## 1. Diagnostic de la Vision (Gemini Vision)

Si les agents échouent à analyser une image ou une vidéo, vous pouvez tester le capteur en isolation.

- **Procédure** : Utilisez le `VisionResourceTool` avec une requête simple.
- **Vérification** :
    - Vérifiez que le chemin de l'image est correct (relatif à la racine).
    - Vérifiez que l'API Key a les droits pour le modèle `gemini-1.5-flash`.
- **Exemple de test** :
```python
from src.tools.vision_tool import VisionResourceTool
tool = VisionResourceTool()
print(tool._run(image_path="resources/VOTRE_IMAGE.png", query="Décris cette image."))
```

## 2. Diagnostic des Outils MCP (Playwright)

Les outils de découverte (`InspectPageTool`, `ListFilesTool`) peuvent être testés sans lancer tout le Crew.

### Exploration du DOM
Pour vérifier ce que l'IA "voit" sur une page web :
```python
from src.tools.playwright_mcp import InspectPageTool
tool = InspectPageTool()
print(tool._run(url="https://votre-site.com"))
```
*Note : Cela retourne un JSON des éléments interactifs avec leurs locateurs Aria suggérés.*

### Discovery Disque
Pour vérifier si le framework accède bien à vos ressources :
```python
from src.tools.playwright_mcp import ListFilesTool
tool = ListFilesTool()
print(tool._run(directory="resources"))
```

## 3. Debug de l'Intégration Xray (API REST & GraphQL)

### Erreur 400 sur l'Import
Si l'import d'une feature échoue avec une erreur 400, il s'agit souvent d'un problème de `Project Key`.
- **Validation** : Assurez-vous que le paramètre `--project` passé à `main.py` correspond exactement au préfixe de vos tickets dans Jira (ex: `SCRUM`).

### Liaison Avancée (Test Set / Pre-Condition)
L'importation via `/import/feature` ne lie pas toujours automatiquement les tests aux Test Sets. Le framework utilise une session GraphQL complémentaire pour garantir cette liaison.

**Schéma de liaison GraphQL** :
```graphql
mutation {
    addTestsToTestSet(
        issueId: "ID_DU_TEST_SET",
        testIssueIds: ["ID_DU_TEST"]
    ) {
        addedTests
    }
}
```

## 4. Performance et Quotas

### Pourquoi c'est "lent" ?
- **Pauses de Quota** : Par défaut, une pause de **20 secondes** est observée après chaque tâche pour éviter d'exploser les RPM (Requests Per Minute) sur les comptes gratuits.
- **Initialisation du Cache** : Au démarrage, le système prend ~15s pour uploader et figer le Wiki sur les serveurs de Google (Context Caching).

> [!TIP]
> Pour accélérer les tests locaux, vous pouvez réduire la variable `MAX_RPM` dans `src/config.py` si vous possédez un compte Gemini payant (Tier 1+).
