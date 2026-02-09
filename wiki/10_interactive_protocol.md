# Protocole Intéractif "Human-in-the-Loop"

Le Labo QA IA ne fonctionne pas en "boîte noire". Il utilise un modèle de validation interactive où l'utilisateur est sollicité aux étapes clés pour garantir que l'automatisation reflète parfaitement les besoins métiers.

## 1. L'Outil `ask_human`

Tous les échanges passent par l'outil `HumanInputTool`. Lorsqu'un agent a besoin d'une validation :
1.  Il suspend son exécution.
2.  Il affiche sa question ou sa proposition dans le terminal.
3.  Il attend une saisie utilisateur.
4.  Il reprend son raisonnement basé sur votre réponse.

## 2. Les Portes de Validation (Gates)

Il existe deux points de contrôle critiques :

### Gate 1 : Validation des Règles (Analyste -> Interviewer)
- L'**Analyste** produit un brouillon des règles de gestion.
- Le **Requirement Interviewer** vous les présente point par point.
- **Actions possibles** : 
    - `OK` : Pour valider une règle.
    - `FIX [détail]` : Pour demander une correction immédiate.
    - `ADD [règle]` : Pour ajouter une règle manquante.

### Gate 2 : Validation du Design & JDD (Designer -> Interviewer)
- Le **Designer** crée les scénarios Gherkin et propose des Jeux de Données (JDD).
- Le **Design Interviewer** valide avec vous le flux logique (Given/When/Then) puis les valeurs des tables `Examples`.

## 3. La "BOUCLE DE SÉCURITÉ" (Safety Loop)

Pour le **Design Interviewer**, une règle de sécurité stricte a été implémentée :
- L'agent **DOIT** présenter le fichier Gherkin complet à la fin.
- L'agent **NE PEUT PAS** terminer sa tâche sans avoir reçu un **"GO"** explicite de votre part.
- Si vous demandez un résumé, une modification ou si vous émettez une critique, l'agent reste dans sa boucle et doit re-demander le "GO" après avoir intégré vos remarques.

> [!IMPORTANT]
> Cette boucle garantit que le SDET ne commence jamais à coder sur un design non-approuvé.
