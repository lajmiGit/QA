# Architecture Playwright + MCP (Model Context Protocol)

Mise en situation : En tant qu'expert **Playwright & MCP**, voici comment nous pourrions restructurer l'écriture et l'exécution du code pour une autonomie totale.

## 1. Qu'est-ce que MCP ?

Le **Model Context Protocol (MCP)** est un standard ouvert qui permet aux LLM (modèles d'IA) de se connecter à des données et des outils externes via des serveurs standardisés.

*   **Aujourd'hui** : Votre script `main.py` est un "chef d'orchestre" rigide. Il attend que l'IA finisse de parler, prend son JSON, et exécute le travail.
*   **Avec MCP** : L'IA devient "l'ouvrier qualifié". Elle a des bras (Tools) connectés directement à votre machine. Elle n'attend pas la fin de la conversation pour agir, elle agit *pendant* la conversation.

## 2. Nouvelle Architecture Proposée

Au lieu d'avoir un `FileManager` python codé en dur, nous utiliserions un **Serveur MCP Filesystem** et un **Serveur MCP Playwright**.

### Les Composants

1.  **MCP Server - Filesystem** : Spécialisé dans l'écriture sécurisée de fichiers.
2.  **MCP Server - Playwright** : Spécialisé dans le pilotage du navigateur et l'exécution de tests.
3.  **MCP Client (Votre Agent)** : Connecté à ces deux serveurs.

## 3. Workflow : "Comment gérer l'écriture du code ?"

Voici le scénario détaillé d'une création de test avec MCP.

### Étape 1 : Conception (Intention)
L'agent SDET analyse la demande (`SCRUM-8`). Il décide qu'il faut créer un fichier de test.

### Étape 2 : Écriture Directe (Action)
Au lieu de retourner du texte JSON à `main.py`, l'Agent appelle **directement** l'outil MCP.

> **Agent** : "Je vais créer le fichier de test."
> **Tool Call** : `filesystem.write_file({ path: "automation/tests/cart.spec.ts", content: "..." })`

Le *Serveur MCP Filesystem* reçoit l'ordre, vérifie les permissions, écrit le fichier et répond à l'agent :
> **MCP Server** : "Succès. 2405 octets écrits."

### Étape 3 : Exécution / Debug (Feedback Loop)
L'Agent peut immédiatement tester son code sans intervention humaine.

> **Agent** : "Maintenant je lance le test pour vérifier."
> **Tool Call** : `playwright.run_test({ testFile: "cart.spec.ts" })`

Le *Serveur MCP Playwright* lance le navigateur. Si ça échoue, il renvoie les logs d'erreur à l'agent.

> **MCP Server** : "Erreur: TimeoutWaitingForSelector '.btn-checkout'"

### Étape 4 : Auto-Correction (Self-Healing)
L'Agent lit l'erreur, comprend le problème, et rappelle l'outil d'écriture.

> **Agent** : "Ah, le sélecteur est mauvais. Je le corrige."
> **Tool Call** : `filesystem.write_file(...)` (Mise à jour)

## 4. Comparatif : Main.py vs MCP

| Critère | Approche Actuelle (`main.py`) | Approche MCP |
| :--- | :--- | :--- |
| **Contrôle** | L'humain (via le script Python) contrôle le flux. | L'IA a l'autonomie d'appeler les outils quand elle veut. |
| **Flexibilité** | Faible. Si on veut ajouter un outil, il faut recoder `main.py`. | Haute. On ajoute juste un Serveur MCP (ex: GitHub MCP) et l'agent l'utilise. |
| **Feedback** | Lent. On attend la fin de toute la génération pour tester. | Immédiat. L'agent teste ligne par ligne s'il le souhaite. |
| **Complexité** | Simple (Code impératif). | Élevée (Gestion d'état asynchrone, boucles infinies potentielles). |

## 5. Conclusion d'Expert

Passer à MCP transforme votre projet d'une **"Chaîne de production automatisée"** (Linéaire) à un **"Ingénieur Virtuel Autonome"** (Dynamique).

C'est l'avenir pour gérer des bases de code complexes, car l'agent peut explorer le dossier, lire les fichiers existants pour comprendre le contexte, et écrire le nouveau code en respectant le style existant, le tout sans que vous ayez à coder la logique de lecture/écriture dans votre orchestrateur.
