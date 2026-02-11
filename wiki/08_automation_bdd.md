# Architecture d'Automatisation BDD (Phase 3)

Le Labo QA IA intègre désormais une stack d'automatisation complète basée sur **Playwright** et **BDD (Behavior Driven Development)**.

## 1. Vue d'Ensemble

L'objectif est de transformer les scénarios Gherkin générés par l'IA en tests exécutables sans intervention manuelle lourde.

**Flux de Données :**
`Agent SDET` → `Fichiers (.feature, .ts)` → `bddgen` → `Playwright` → `Rapport`

## 2. Structure du Dossier `automation/`

Le dossier `automation/` est un projet Node.js/TypeScript autonome.

-   **`features/`** : Contient les fichiers `.feature` (Gherkin). C'est la **Source de Vérité**.
-   **`src/steps/`** : Contient les *Step Definitions* (`.steps.ts`). C'est le code qui fait le lien entre le Gherkin et Playwright.
-   **`src/pages/`** : Contient les *Page Objects* (`.page.ts`). Encapsule la logique d'interaction avec l'UI (sélecteurs, actions).
-   **`src/fixtures/`** : Contient les fixtures Playwright (`index.ts`) pour l'injection de dépendances (Pages, Actors).
-   **`.features-gen/`** : Dossier généré automatiquement par `bddgen`. Il contient les tests techniques Playwright (`.spec.js`) dérivés des features. **Ne pas modifier manuellement.**
-   **`playwright.config.ts`** : Configuration globale.
    -   **`slowMo: 500`** : Un délai de 500ms est ajouté entre chaque action pour faciliter le suivi visuel.
    -   **`retries: 2`** : Les tests instables sont relancés automatiquement.

## 3. Workflow BDD

### A. Génération
L'agent SDET génère trois types de contenu pour chaque User Story :
1.  Le fichier `.feature` (avec tags Jira/Xray).
2.  Le fichier Page Object (ex: `modifyBasketItemQuantity.page.ts`).
3.  Le fichier Step Definitions (ex: `modify-item-quantity.steps.ts`).

### B. Compilation (bddgen)
L'outil `playwright-bdd` est utilisé pour "compiler" le Gherkin.
Commande : `npx bddgen`
Effet : Lit `features/*.feature` et `steps/*.ts`, puis génère des tests exécutables dans `.features-gen/`.

### C. Exécution
Les tests sont lancés via Playwright standard.
Commande : `npx playwright test`

### D. Diagnostic Visuel & Mémanence
En cas d'échec, le système utilise Gemini Vision pour analyser l'écran (screenshot/vidéo). Des délais de sécurité (`await this.page.waitForTimeout(3000)`) sont intégrés dans les Page Objects lors de la récupération des messages d'erreur pour garantir que le DOM est stabilisé avant la lecture.

## 4. Maintenance

-   **Changement de Règle Métier** : Mettre à jour le `.feature` (et les steps si nécessaire).
-   **Changement d'UI (Sélecteur)** : Mettre à jour uniquement le fichier Page Object dans `src/pages/`.
-   **Nouveau Step Gherkin** : Ajouter la définition dans `steps/`.

## 5. Dépannage Courant

-   *Error: Missing step definition* : Le Gherkin utilise une phrase qui n'a pas de correspondance exacte dans les fichiers `steps/*.ts`. Vérifiez la syntaxe ou créez le step manquant.
-   *Error: Connection Refused* : L'application cible (ex: `localhost:3000`) n'est pas lancée. C'est normal si vous testez uniquement le code de test.
