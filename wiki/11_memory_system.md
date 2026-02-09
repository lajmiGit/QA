# Système de Mémoire (Long-Term Memory)

Le Labo QA IA possède une mémoire persistante qui lui permet d'apprendre de chaque exécution et de proposer des suggestions pertinentes basées sur l'historique du projet.

## 1. La `knowledge_base.json`

C'est le fichier physique où sont stockées les connaissances. Il est structuré par clés :
- `validated_rules` : Liste des règles métier déjà approuvées.
- `preferred_jdd` : Valeurs par défaut pour les tests (ex: comptes de test, URLs spécifiques).
- `project_conventions` : Nommage, patterns de code préférés.

## 2. Les Outils de Connaissance

### `query_knowledge`
Utilisé par les agents au début d'une tâche pour consulter l'historique. 
- *Exemple* : Le Designer consulte les `preferred_jdd` pour proposer le même utilisateur "john" que lors des tests précédents.

### `update_knowledge`
Utilisé par les agents à la fin d'une validation réussie pour mémoriser les nouveaux éléments.
- *Condition* : La mise à jour n'a lieu qu'APRÈS avoir reçu le "GO" final de l'utilisateur.

## 3. Avantages du Système
1.  **Consistance** : Les tests gardent la même structure et les mêmes données à travers les versions.
2.  **Productivité** : Moins de saisie pour l'utilisateur, car le système propose des valeurs "par défaut" déjà validées.
3.  **Apprentissage** : Plus le labo est utilisé, plus il devient autonome et pertinent dans ses propositions.

> [!TIP]
> Vous pouvez consulter ou éditer manuellement le fichier `knowledge_base.json` à la racine pour "pré-charger" des connaissances ou corriger une mémorisation.
