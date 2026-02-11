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
| **`list_files`** | [ENHANCED] Lister les fichiers avec métadonnées (`name`, `mtime`, `size`). Permet l'analyse incrémentale. | Analyst, SDET |
| **`run_playwright_test`** | Lancer les tests (tous ou fichier spécifique). Retourne les logs. | SDET |
| **`inspect_page`** | [ENHANCED] Extraire le DOM riche (Rôles Aria, Noms Accessibles) et suggérer des locateurs Playwright. | SDET |
| **`take_screenshot`** | Capturer une image pour le debugging visuel. | SDET |
| **`get_console_logs`** | Récupérer les erreurs JS de la console navigateur. | SDET |
| **`explore_page_with_actions`** | [ENHANCED] Naviguer, agir puis inspecter le DOM avec Vision Sémantique. | SDET (Interactif) |

## 3. Vision Sémantique & Locateurs Robustes [NEW]

Le serveur MCP a été amélioré pour fournir une "Vision Sémantique" à l'IA :
- **Extraction des Rôles Aria** : Identifie les composants par leur fonction (button, link, heading) plutôt que par leur balise HTML.
- **Accessible Names** : Capture le texte réel perçu par l'utilisateur (labels, placeholders).
- **Playwright Locator Generator** : L'outil renvoie directement des suggestions de code comme `page.getByRole('button', { name: 'Login' })`, garantissant un code de test plus stable et lisible.

## 3. Optimisations Temp-Réel & Diagnostic

### Élimination du Cache [NEW]
Pour éviter que les agents ne travaillent sur des données obsolètes (ex: un échec de test persistant en mémoire alors que le code a été corrigé), le cache CrewAI a été désactivé pour les outils de diagnostic :
- `run_playwright_test`
- `take_screenshot`
- `inspect_page`
- `get_console_logs`
- `write_file`

### Centralisation des Ressources (`/resources`) [NEW]
Afin de séparer les actifs métier des résultats de tests temporaires :
- **Entrées** : Les agents cherchent les maquettes et vidéos dans le dossier racine `/resources`.
- **Sorties Agents** : Les captures d'écran demandées par les agents (`Analyst`, `Interviewer`) sont automatiquement redirigées vers `/resources` (via un chemin relatif `../resources/` géré par le client MCP).
- **Isolation Playwright** : Les enregistrements liés à l'exécution technique des tests restent dans `automation/test-results/`.

## 4. Workflow SDET Interactif & Vision-First

Grâce à cette architecture, l'agent SDET ne code plus "à l'aveugle".

1.  **Exploration** : L'agent utilise `explore_page_with_actions` pour atteindre une page sécurisée (ex: Dashboard après Login).
2.  **Inspection** : Le serveur MCP pilote Playwright pour effectuer les actions et renvoie le HTML réel.
3.  **Codage** : L'agent génère le Page Object avec des sélecteurs vérifiés.
4.  **Validation** : L'agent lance `run_playwright_test` pour confirmer.

## 5. Démarrage Technique

Le serveur est démarré automatiquement par le client Python (`src/tools/playwright_mcp.py`), mais peut être testé manuellement :

```bash
cd automation
npm run start:mcp
```
