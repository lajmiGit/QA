# Structure du Projet et Configuration

Cette section décrit l'organisation des fichiers et la configuration initiale du Labo QA IA.

## Arborescence du Projet

Nous avons structuré le projet de manière modulaire pour séparer la logique des agents, les outils et les artefacts générés.

```text
qa_labo_ia/
├── .env                  # Fichier de configuration (clés API) - À NE PAS COMMITER
├── .env.example          # Modèle du fichier de configuration
├── main.py               # Point d'entrée principal pour lancer le Crew
├── src/
│   ├── agents.py         # Définition des agents (Analyste, Designer, SDET, Superviseur)
│   ├── tasks.py          # Définition des tâches assignées aux agents
│   └── tools/            # Outils personnalisés (Xray, Jira)
├── automation/           # Projet Playwright BDD
│   ├── features/         # Fichiers Gherkin (.feature) - Source de vérité
│   ├── steps/            # Définitions des étapes (.steps.ts)
│   ├── src/pages/        # Page Object Model (.page.ts)
│   ├── .features-gen/    # Tests générés par bddgen
│   └── playwright.config # Configuration Playwright
├── output/               # (Obsolète) Anciens fichiers générés
└── tests/                # (Obsolète) Anciens tests Playwright
```

## Configuration des Variables d'Environnement

Le projet utilise `python-dotenv` pour gérer les secrets.

1.  Créez un fichier nommé `.env` à la racine du projet.
2.  Ajoutez votre clé API Google Gemini :

```ini
GOOGLE_API_KEY=votre_cle_api_ici
```

**Note** : Ce fichier contient des informations sensibles et est ignoré par Git.
