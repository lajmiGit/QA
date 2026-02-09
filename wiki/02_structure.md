# Structure du Projet et Configuration

Cette section décrit l'organisation des fichiers et la configuration initiale du Labo QA IA.

## Arborescence du Projet

Nous avons structuré le projet de manière modulaire pour séparer la logique des agents, les outils et les artefacts générés.

```text
qa_labo_ia/
├── .env                  # Fichier de configuration (clés API) - À NE PAS COMMITER
├── .env.example          # Modèle du fichier de configuration
├── knowledge_base.json   # Base de connaissances persistante (LTM)
├── main.py               # Point d'entrée principal pour lancer le Crew
├── src/
│   ├── agents.py         # Définitions des agents (Analyste, Interviewers, Designer, etc.)
│   ├── tasks.py          # Définitions des tâches (Analysis, Interview, Design, etc.)
│   └── tools/
│       ├── jira_tool.py      # Connecteur Jira Cloud
│       ├── xray_tool.py      # Connecteur Xray Cloud
│       ├── knowledge_tool.py # Outils de lecture/écriture de la mémoire
│       └── human_tool.py     # Outil d'interaction utilisateur (ask_human)
├── automation/           # Projet Playwright BDD (Clean Slate Expert)
│   ├── features/         # Fichiers Gherkin (.feature) - Source de vérité
│   ├── src/              # Code source unifié
│   │   ├── pages/        # Page Object Model (.page.ts)
│   │   ├── steps/        # Définitions des étapes (.steps.ts)
│   │   ├── fixtures/     # Injection de dépendances (index.ts)
│   │   └── utils/        # Fonctions utilitaires
│   └── playwright.config.ts # Configuration Playwright
├── output/               # Journaux d'exécution et résultats finaux
├── wiki/                 # Documentation complète du projet
```

## Configuration des Variables d'Environnement

Le projet utilise `python-dotenv` pour gérer les secrets.

1.  Créez un fichier nommé `.env` à la racine du projet.
2.  Ajoutez votre clé API Google Gemini :

```ini
GOOGLE_API_KEY=votre_cle_api_ici
```

**Note** : Ce fichier contient des informations sensibles et est ignoré par Git.

---

## Documentation Complémentaire : Validation & Mémoire

Pour approfondir les nouveaux concepts d'interaction et de mémorisation :
- [10_interactive_protocol.md](file:///Users/lajmi/Documents/qa_labo_ia/wiki/10_interactive_protocol.md) : Détails sur le protocole "Human-in-the-Loop" et la porte de sécurité.
- [11_memory_system.md](file:///Users/lajmi/Documents/qa_labo_ia/wiki/11_memory_system.md) : Fonctionnement de la base de connaissances persistante.
