# Installation et Configuration de l'Environnement

Ce guide détaille les étapes pour configurer l'environnement de développement pour utiliser CrewAI avec Gemini.

## Packages Installés

Nous avons installé les bibliothèques suivantes :

1.  **`crewai`** : Un framework permettant d'orchestrer des agents IA autonomes capables de collaborer pour résoudre des tâches complexes.
2.  **`langchain-google-genai`** : L'intégration officielle permettant d'utiliser les modèles Google Gemini au sein de l'écosystème LangChain.
3.  **`python-dotenv`** : Un utilitaire pour charger les variables de configuration (comme les clés API) depuis un fichier `.env`, assurant la sécurité et la flexibilité du projet.

## Procédure d'Installation

### 1. Création d'un environnement virtuel
Il est recommandé d'utiliser un environnement virtuel pour isoler les dépendances du projet et éviter les conflits avec d'autres projets Python.

```bash
python3 -m venv .venv
```

### 2. Obtention de la clé API Google (Gemini)
Pour utiliser le modèle, vous devez récupérer une clé d'API gratuite :

1.  Connectez-vous à **[Google AI Studio](https://aistudio.google.com/)**.
2.  Cliquez sur le bouton **"Get API key"** dans le menu de gauche.
3.  Cliquez sur **"Create API key"** (vous pouvez l'associer à un projet Google Cloud existant ou en créer un nouveau).
4.  Copiez la clé générée (elle commence généralement par `AIza...`).
5.  Créez un fichier `.env` à la racine de votre projet et collez-y la clé :
    ```ini
    GOOGLE_API_KEY=votre_clé_ici
    ```

### 3. Obtention des accès Jira & Xray (Optionnel)
Pour connecter le labo à vos outils de gestion de tests :

1.  **Jira** : Créez un **API Token** dans votre compte Atlassian (Profil > Sécurité > Create API Token).
2.  **Xray** : Récupérez votre **Client ID** et **Client Secret** depuis les paramètres d'API de Xray Cloud.
3.  Ajoutez ces informations dans votre fichier `.env` :
    ```ini
    # Jira
    JIRA_URL=https://votre-instance.atlassian.net
    JIRA_USER_EMAIL=votre-email@exemple.com
    JIRA_API_TOKEN=votre_token_jira

    # Xray
    XRAY_CLIENT_ID=votre_client_id
    XRAY_CLIENT_SECRET=votre_client_secret
    ```

### 4. Installation des dépendances
Une fois l'environnement créé, nous installons les packages nécessaires :

```bash
.venv/bin/pip install crewai langchain-google-genai python-dotenv atlassian-python-api
```

### 5. Installation du Module d'Automatisation (Playwright BDD)
Pour exécuter les tests générés, vous devez initialiser le projet Node.js :

```bash
cd automation
npm install
npx playwright install
cd ..
```

### 6. Démarrage du Serveur MCP (Critique)
Le système repose sur un serveur MCP pour les outils Playwright. Il doit être lancé avant ou par le script principal (automatique), mais pour le debug :

```bash
cd automation
npm run start:mcp
```

## Vérification

1.  **Python** :
    ```bash
    .venv/bin/python3 -c "import crewai; print('Python OK')"
    ```
2.  **Playwright** :
    ```bash
    cd automation && npx playwright --version
    ```
