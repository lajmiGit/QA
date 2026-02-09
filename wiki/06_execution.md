# Guide d'Exécution

Ce guide explique comment lancer le Labo QA IA pour transformer une User Story en tests automatisés.

## Pré-requis

Assurez-vous d'avoir suivi le guide d'installation et configuré votre fichier `.env` avec la clé API `GOOGLE_API_KEY`.

## Lancement du Cycle QA

Pour lancer le cycle complet (Analyse -> Design -> Code -> Revue), exécutez la commande suivante depuis la racine du projet :

```bash
.venv/bin/python3 main.py --issue SCRUM-272
```

## Déroulement

1.  **Initialisation** : Le script charge les agents et le modèle Gemini.
2.  **Input** : Une User Story est injectée (via `--issue` et `--project`).
3.  **Analyse** : L'agent Analyste décortique l'US.
4.  **Design** : L'agent Designer crée les scénarios Gherkin.
5.  **Développement (BDD)** : L'agent SDET génère le Feature File, les Steps Definitions et le Page Object.
6.  **Automatisation** : Le `FileManager` déploie les fichiers dans le dossier `automation/`.
7.  **Exécution** : `bddgen` compile les tests et Playwright les exécute.
8.  **Revue** : L'agent Superviseur valide le travail et déclenche l'export Xray si succès.

## Résultats

## Résultats
- Les logs d'exécution s'affichent dans le terminal.
- Le résultat final consolidé : `output/final_result_ISSUE-KEY.md`.
- Les fichiers de test générés : `automation/features/`, `automation/steps/`, `automation/src/pages/`.
- Le rapport d'exécution Playwright (si échec ou demande).
