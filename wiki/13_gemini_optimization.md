# Optimisation Gemini : Stratégie Triple-Piliers

Pour garantir la robustesse du Labo QA IA face aux quotas API (Erreurs 429) et réduire les coûts opérationnels, nous avons implémenté une stratégie d'optimisation en trois axes.

## 1. Hybrid Modeling (Répartition de la Charge)

Nous ne traitons plus toutes les tâches avec le même modèle. La charge est répartie selon la complexité :

- **Gemini Pro (`MODEL_PRO`)** : 
    - *Usage* : Raisonnement complexe, génération de code TypeScript, supervision finale.
    - *Modèles* : `gemini-3-pro-preview` ou versions stables.
- **Gemini Flash (`MODEL_FLASH`)** : 
    - *Usage* : Analyse de logs, parsing JSON, Dialogue utilisateur, exploration Playwright.
    - *Avantage* : 10x moins cher, latence ultra-faible, quota TPM (Tokens Per Minute) beaucoup plus élevé.

## 2. Context Trimming (Substance Structurée)

Au lieu de faire circuler des blocs de texte brut massifs entre les agents, nous utilisons des **Modèles Pydantic**.

- **Structure Stricte** : Chaque agent produit un objet JSON validé par Pydantic (ex: `RuleInventory`, `CodeGenerationOutput`).
- **Impact** : Réduction du bruit textuel de 60-80%. Seule la substance utile est transmise à l'agent suivant, préservant ainsi la fenêtre de contexte et les quotas.

## 3. Double-Caching & Savoir Hybride

L'innovation majeure réside dans la gestion de la connaissance via le **Gemini Context Caching**.

### Le Double Cache Serveur
Nous maintenons deux caches persistants (Pro et Flash) contenant l'intégralité du **Wiki** technique du projet. 
- **Wiki dans le Cache** : L'expertise sur "comment coder un Page Object" ou "comment fonctionne la boucle de debug" est stockée une seule fois sur les serveurs de Google.
- **Économie** : Zéro token d'entrée consommé pour lire le Wiki lors des appels agents.

### Hybrid Knowledge (Wiki vs Brain)
Le savoir est injecté dynamiquement :
- **Wiki** : Dans le cache serveur (Expertise technique immuable).
- **Project Brain** : Dans le prompt direct (Mémoire vive et règles métier changeantes).

## 📊 Résultats Observés
- **Réduction des Tokens d'Entrée** : ~70% sur les sessions longues.
- **Stabilité** : Disparition des erreurs 429 lors des analyses multicouches.
- **Vitesse** : Initialisation instantanée car l'agent possède déjà sa base de connaissances au premier token.

> [!IMPORTANT]
> Le cycle de vie des caches est géré par le `GeminiContextManager` dans `src/utils/gemini_cache.py`.
