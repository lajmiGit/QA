# Système de Mémoire (Long-Term Memory)

Le Labo QA IA possède une mémoire persistante qui lui permet d'apprendre de chaque exécution et de proposer des suggestions pertinentes basées sur l'historique du projet.

## 1. Le "Cerveau" du Projet (`project_brain.md`)

C'est le document dynamique qui contient la mémoire vive du projet. Il est structuré pour être lu rapidement par les agents et contient :
- **Registre des Ressources** : Historique des fichiers analysés et leurs `mtime`.
- **Règles Validées** : Directives métier extraites des User Stories passées.
- **Historique des Choix** : URLs, sélecteurs persistants, etc.

## 2. Gemini Context Caching (Double Cache) [OPTIMISÉ]

Pour réduire drastiquement la consommation de tokens et améliorer la latence, nous utilisons le **Context Caching** natif de Gemini.

- **Double Cache** : Nous créons deux caches distincts sur les serveurs de Google :
    - Un cache pour le modèle **Pro** (Raisonnement).
    - Un cache pour le modèle **Flash** (Exploration).
- **Contenu du Cache** : Seul le **Wiki** technique (statique) est mis en cache. Cela donne aux agents une expertise immédiate sur le framework sans consommer de tokens d'entrée à chaque appel.
- **TTL (Time To Live)** : Les caches sont configurés avec une durée de vie de 1 heure et sont systématiquement nettoyés en fin d'exécution (`cleanup`).

## 3. Stratégie de Savoir Hybride (Hybrid Knowledge)

La connaissance est injectée aux agents de deux manières complémentaires :

1.  **Wiki (Statique / Cache)** : L'expertise technique du projet est dans le cache serveur. Coût token = **0** à l'exécution.
2.  **Cerveau (Dynamique / Prompt)** : Le fichier `project_brain.md` est lu en temps réel et injecté directement dans le prompt. Cela garantit que les changements récents (nouvelle règle validée il y a 5 minutes) sont immédiatement pris en compte.

## 4. Outils de Connaissance

- **`query_knowledge`** : Interroge le "Cerveau" et le "Cache" pour répondre à une question métier.
- **`update_knowledge`** : Met à jour la section pertinente du `project_brain.md` (Registre ou Règles).

> [!NOTE]
> Le "Clean Start" au démarrage de `main.py` assure que les caches sont toujours synchronisés avec la dernière version du Wiki.
