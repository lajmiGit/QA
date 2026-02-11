# Plan d'Implémentation : Labo QA IA (CrewAI + Playwright)

Ce document décrit le plan technique pour l'implémentation du Labo QA IA autonome utilisant CrewAI et Gemini.

## Objectif
Créer un système multi-agents capable de transformer une User Story en script de test Playwright exécutable.

## Architecture des Agents (CrewAI)

Nous allons implémenter 4 agents distincts dans `agents.py` (ou des fichiers séparés) :

1.  **Analyste QA (`analyst`)**
    *   **Rôle** : Analyser les User Stories (US).
    *   **Goal** : Identifier les règles de gestion, les critères d'acceptation et les flux.
    *   **Output** : Document d'analyse structuré.

2.  **Designer de Tests (`designer`)**
    *   **Rôle** : Créer les scénarios de test.
    *   **Goal** : Traduire l'analyse en scénarios Gherkin (.feature).
    *   **Output** : Fichier `.feature`.

3.  **Ingénieur SDET (`sdet`)**
    *   **Rôle** : Implémenter le code d'automatisation.
    *   **Goal** : Générer le code TypeScript Playwright (POM) correspondant au Gherkin.
    *   **Output** : Fichiers `.ts` (Page Objects et Specs).

4.  **Superviseur (`supervisor`)**
    *   **Rôle** : Revue de code et qualité.
    *   **Goal** : Vérifier la cohérence du code produit, s'assurer que ça compile (théoriquement/visuellement) et respecte les bonnes pratiques.
    *   **Output** : Rapport de validation ou demande de correction.

## Structure du Projet

```text
qa_labo_ia/
├── .env                  # Clés API (GOOGLE_API_KEY)
├── main.py               # Point d'entrée pour lancer le Crew
├── src/
│   ├── agents.py         # Définition des agents
│   ├── tasks.py          # Définition des tâches
│   └── tools/            # Outils personnalisés (ex: FileReadTool, FileWriteTool)
├── output/               # Dossier pour les artefacts générés (Gherkin, Code)
└── tests/                # Dossier cible pour les tests Playwright générés
```

## Étapes d'Implémentation

### 1. Configuration Initiale
*   Créer l'arborescence des dossiers.
*   Créer le fichier `.env` (template).

### 2. Définition des Agents et Tâches (`src/`)
*   Implémenter `src/agents.py` avec `crewai.Agent`.
*   Implémenter `src/tasks.py` avec `crewai.Task`.
*   Configurer le modèle Gemini via `langchain_google_genai`.

### 3. Orchestration (`main.py`)
*   Configurer le `Crew` avec les agents et les tâches.
*   Définir le processus (séquentiel).
*   Lancer l'exécution avec une User Story d'exemple (US01).

### 4. Outils (Tools)
*   Besoin d'outils pour que les agents puissent écrire les fichiers (`.feature`, `.ts`).
*   Utilisation de `crewai_tools` ou création de custom tools pour l'écriture de fichiers.

## Vérification
*   Lancer `python main.py`.
*   Vérifier que les fichiers sont générés dans `output/` ou `tests/`.
*   Vérifier la qualité du code généré.
