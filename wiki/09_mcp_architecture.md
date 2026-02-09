# Architecture Playwright + MCP (Model Context Protocol)

Ce document décrit l'architecture technique mise en place pour permettre aux agents IA de manipuler le projet d'automatisation.

## 1. Vue d'Ensemble

Le projet utilise le standard **Model Context Protocol (MCP)** pour connecter les agents CrewAI (Python) aux capacités d'automatisation (Node.js/Playwright).

*   **Python (CrewAI)** : Le "Cerveau". Orchestre les agents.
*   **MCP Server (Node.js)** : Les "Mains". Situé dans `automation/src/mcp-server.ts`.
*   **StdIO Transport** : La communication se fait via l'entrée/sortie standard du processus Node.js.

## 2. Le Serveur MCP (`automation/src/mcp-server.ts`)

Ce serveur expose une collection d'outils que les agents peuvent appeler directement.

### Liste des Outils Disponibles

| Outil | Description | Utilisateur Principal |
| :--- | :--- | :--- |
| **`write_file`** | Créer ou modifier un fichier (Features, Pages, Steps). | SDET |
| **`read_file`** | Lire un fichier existant pour l'analyser. | SDET, Supervisor |
| **`list_files`** | Lister l'arborescence pour comprendre la structure. | Analyst, SDET |
| **`run_playwright_test`** | Lancer les tests (tous ou fichier spécifique). Retourne les logs. | SDET |
| **`inspect_page`** | Extraire le DOM simplifié d'une page publique. | SDET |
| **`take_screenshot`** | Capturer une image pour le debugging visuel. | SDET |
| **`get_console_logs`** | Récupérer les erreurs JS de la console navigateur. | SDET |
| **`explore_page_with_actions`** | [NEW] Naviguer, agir (click/fill) puis inspecter le DOM (State-Aware). | SDET (Interactif) |

## 3. Workflow SDET Interactif

Grâce à cette architecture, l'agent SDET ne code plus "à l'aveugle".

1.  **Exploration** : L'agent utilise `explore_page_with_actions` pour atteindre une page sécurisée (ex: Dashboard après Login).
2.  **Inspection** : Le serveur MCP pilote Playwright pour effectuer les actions et renvoie le HTML réel.
3.  **Codage** : L'agent génère le Page Object avec des sélecteurs vérifiés.
4.  **Validation** : L'agent lance `run_playwright_test` pour confirmer.

## 4. Démarrage Technique

Le serveur est démarré automatiquement par le client Python (`src/tools/playwright_mcp.py`), mais peut être testé manuellement :

```bash
cd automation
npm run start:mcp
```
