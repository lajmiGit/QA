from crewai import Task
from textwrap import dedent
from src.models import RuleInventory, GherkinDesign

class LaboQaTasks:

    def analysis_task(self, agent, user_story_context=None, direct_input=None):
        description = dedent("""
            ÉTAPE 0 : CONSULTATION DU CERVEAU (OBLIGATOIRE)
            - Interrogez le 'Cerveau du Projet' via `query_knowledge` en posant une question précise en langage naturel sur les règles déjà validées ou l'historique de cette fonctionnalité. Ne redéfinissez pas ce qui est déjà acté.
            
            ÉTAPE CRITIQUE : DISCOVERY VISUELLE CIBLÉE (OBLIGATOIRE)
            1. LISTE DES RESSOURCES : Appelez l'outil 'list_files' sur le dossier 'resources/' pour voir les dossiers disponibles (ex: SCRUM-326, SCRUM-189).
            2. CHOIX DE L'UTILISATEUR : Appelez l'outil 'ask_human' en présentant la liste des dossiers trouvés et demandez : "Dans quel dossier spécifique (ex: resources/SCRUM-XXX) dois-je effectuer l'analyse visuelle pour ce ticket ?".
            3. ANALYSE SÉLECTIVE : Une fois le dossier confirmé (ex: 'resources/SCRUM-326'), listez les fichiers de CE DOSSIER UNIQUEMENT.
            4. INTERROGATION DE LA MÉMOIRE : Consultez le 'Cerveau du Projet' via `query_knowledge` pour récupérer le "Registre des Ressources Analysées" pour ce ticket spécifique.
            5. LOGIQUE DE DÉCISION (PROTOCOLE DELTA) : 
               - Comparez les `mtime` des fichiers du dossier choisi avec ceux en mémoire.
               - Ne lancez 'analyze_resource_image' ou 'analyze_scenario_video' QUE pour les nouveaux fichiers ou ceux modifiés.
            6. MISE À JOUR DU REGISTRE : En fin d'analyse, utilisez `update_knowledge` pour mettre à jour le Registre des Ressources.
            
            PHASE 2 : ANALYSE FONCTIONNELLE
            Une fois (et seulement une fois) que vous avez consolidé l'analyse de toutes les ressources (nouvelles et anciennes), extrayez toutes les NOUVELLES règles ou ajustements de la User Story.
        """)
        if direct_input:
            description += f"\nDonnée d'entrée directe: {direct_input}\n"
        
        description += dedent("""
            INSTRUCTIONS :
            1. Listez TOUTES les règles identifiées.
            2. Catégorisez-les : [EXPLICIT], [SUGGESTION/EDGE_CASE], [MISSING_DATA].
            3. Pour chaque [MISSING_DATA], proposez une valeur par défaut ou une question précise.
            
            IMPORTANT : Produisez une liste numérotée claire. Ce document sera la base de l'interview utilisateur.
        """)
        
        context = [user_story_context] if user_story_context else []
        
        return Task(
            description=description,
            agent=agent,
            context=context,
            expected_output="Inventaire technique structuré (RuleInventory)",
            output_pydantic=RuleInventory
        )

    def interview_analysis_task(self, agent, analysis_context):
        return Task(
            description=dedent("""
                Mener une interview de validation via le **PROTOCOLE DE COLLECTE SÉQUENTIELLE SILENCIEUSE** :
                
                1. **VISION GLOBALE** : Affichez d'abord le tableau Markdown complet des règles.
                2. **COLLECTE POINT PAR POINT** : Posez une question précise via `ask_human` pour chaque ID.
                3. **SILENCE IA (STRICT)** : Interdiction de commenter entre les questions. Soyez sériel.
                4. **CONSOLIDATION** : Une synthèse finale après clôture.
            """),
            agent=agent,
            context=[analysis_context],
            expected_output="Analyse validée point par point sans interférences de l'IA."
        )

    def test_design_task(self, agent, interview_context):
        return Task(
            description=dedent(f"""
                Concevoir les scénarios Gherkin (Scenario Outline).
                
                **CONVENTION DE SYNTAXE DYNAMIQUE (OBLIGATOIRE)** :
                Utilisez les placeholders : `<unique>`, `<email>`, `<adult_dob>`, `<future_date>`.
                Rédigez en anglais.
            """),
            agent=agent,
            context=[interview_context],
            expected_output="Design Gherkin structuré (GherkinDesign)",
            output_pydantic=GherkinDesign
        )

    def interview_design_task(self, agent, design_context):
        return Task(
            description=dedent("""
                Valider le Design Gherkin via le **PROTOCOLE DE COLLECTE SÉQUENTIELLE SILENCIEUSE** :
                1. Affichez le Gherkin complet.
                2. Posez des questions séquentielles sur la logique et les JDD.
                3. Attendez le 'GO'.
            """),
            agent=agent,
            context=[design_context],
            expected_output="Design Gherkin validé efficacement point par point."
        )

    def code_generation_task(self, agent, design_context, xray_context, issue_key=None, base_url=None):
        feature_tag_instruction = ""
        if issue_key:
            feature_tag_instruction = f"- Tu dois insérer le tag de la User Story (@{issue_key}) juste au dessus de 'Feature:'."
            
        from src.models import CodeGenerationOutput

        url_to_inspect = base_url if base_url else "http://localhost:3000/#/"

        return Task(
            description=dedent(f"""
                Tu es un ingénieur autonome. Ta mission est d'implémenter et de VALIDER les tests Playwright pour la User Story.
                
                SOURCE DE VÉRITÉ STRICTE :
                Tu ne reçois PAS tout l'historique de conversation (vidéos, analyses, etc.).
                Tu reçois uniquement un objet `GherkinDesign` contenant :
                1. Le contenu Gherkin validé.
                2. Les exemples de données de test.
                
                **MODE TASK-ONLY** :
                - Ne cherche pas à "deviner" le contexte visuel passé. Si tu as besoin d'infos sur un sélecteur ou une règle, utilise `query_knowledge` pour interroger le "Cerveau du Projet".
                - Si tu as besoin de voir la page actuelle, utilise `inspect_page` ou `explore_page_with_actions`.
                
                **RÈGLE D'IMMUTABILITÉ** : Il est strictement INTERDIT de modifier les scénarios Gherkin pour faire passer un test. Si un test échoue, vous devez corriger le CODE (Page Objects ou Steps) pour qu'il corresponde aux scénarios.
                
                ACTIONS ATTENDUES :
                1.  **AUDIT DU CODE EXISTANT (OBLIGATOIRE)** :
                    - Utilisez `list_files` sur `src/pages/`, `steps/` et `features/`.
                    - **RÈGLE DE SÉCURITÉ TOKENS** : Ne JAMAIS appeler `list_files` sur la racine `.` ou `/` avec l'option récursive. Si vous devez explorer la structure, faites-le dossier par dossier.
                    - Si des fichiers existent déjà pour cette fonctionnalité (ex: `login.page.ts`), utilisez `read_file` pour les analyser.
                    - **RÈGLE ANTI-DUPLICATION** : Si un fichier existe, vous devez le METTRE À JOUR avec `write_file` plutôt que d'en créer un nouveau (exemple: ne créez pas `login_v2.page.ts`).
                
                2.  **ARCHITECTURE BDD STRICTE (playwright-bdd)** :
                    - Ce projet utilise `playwright-bdd`. Vous ne devez PAS créer de fichiers `.spec.ts` ou `.test.ts` manuellement.
                    - Structure cible :
                    - Structure cible :
                      - `features/{issue_key}_{{feature_name}}.feature` : Contient le Gherkin complet (@{{issue_key}} obligatoire).
                      - `src/steps/{{feature_name}}.steps.ts` : Contient les `createBdd` et `Given/When/Then`.
                        - EXEMPLE : `import {{ createBdd }} from 'playwright-bdd'; import {{ test }} from '../fixtures'; const {{ Given, When, Then }} = createBdd(test); ...`
                      - `src/pages/{{feature_name}}.page.ts` : Contient la logique Page Object.
                
                3.  **EXPLORATION DE L'UI (VISION & ACTION)** :
                    - Si de nouveaux éléments sont nécessaires (ex: Dashboard après login), utilisez `explore_page_with_actions` pour atteindre l'état désiré et inspecter le DOM.
                    - Utilisez `inspect_page` pour les pages publiques.
                    - En cas de doute technique, utilisez `ask_human`.
                
                4.  **IMPLÉMENTATION & REFACTORING** :
                    - Injectez les nouveaux sélecteurs et méthodes dans les Page Objects (existant ou nouveau).
                    - Implémentez les Step Definitions dans `steps/` (extension `.steps.ts`) en utilisant `createBdd` de `playwright-bdd`.
                    - **INTERDICTION** : Ne pas mettre de code de test (locators, assertions complexes) directement dans les steps. Appelez les méthodes du Page Object.
                
                5.  **BOUCLE D'AUTONOMIE & VALIDATION (PROTOCOLE RE-INSPECT)** :
                    - Lancez le test avec `run_playwright_test`.
                    - **ANALYSE DES ÉCHECS : SI LE TEST ÉCHOUE, VOUS DEVEZ PROCÉDER COMME SUIT (STRICT) :**
                        a. **RE-NAVIGATION** : Utilisez `explore_page_with_actions` pour atteindre exactement l'état où le test a échoué.
                        b. **INSPECTION TECHNIQUE SÉMANTIQUE** : Appelez `inspect_page` sur l'URL actuelle pour obtenir les nouveaux locateurs (Rôles Aria, Noms Accessibles).
                        c. **AUDIT VISUEL** : Prenez un screenshot (`take_screenshot`) et analysez-le avec `analyze_resource_image` pour confronter la vision IA avec les données techniques du DOM.
                    - **AUTO-CORRECTION** : Appliquez les corrections sur le CODE TypeScript en privilégiant les `suggestedLocator` fournis par l'outil d'inspection (getByRole, getByPlaceholder).
                    - **RÉPÉTITION** : Répétez le cycle jusqu'à ce que 100% des scénarios passent.
                
                LIVRABLES :
                Ne retourne PAS de JSON. Retourne un rapport textuel final ("Rapport de Validation") incluant :
                - Résumé des fichiers mis à jour/créés.
                - Capture du résultat final du test (Playwright output).
                - Liste des problèmes rencontrés et comment ils ont été résolus sans modifier le Gherkin.
            """),
            agent=agent,
            context=[design_context, xray_context],
            expected_output="Un rapport textuel confirmant que les fichiers sont créés et que les tests passent."
        )

    def review_task(self, agent, code_context, design_context, xray_context):
        return Task(
            description=dedent(f"""
                Réviser le code Playwright et les scénarios Gherkin pour en assurer la qualité et la cohérence.
                
                POINTS DE CONTRÔLE:
                1. Le code Playwright est-il valide et complet ?
                2. Les sélecteurs utilisés semblent-ils robustes ?
                3. Le code respecte-t-il le pattern POM ?
                4. Tous les scénarios Gherkin sont-ils couverts par le code ?
                5. RÉSULTAT TECHNIQUE : Le rapport doit confirmer EXPLICITEMENT que l'exécution Playwright est passée à 100% (vérifier output de code_generation_task).
                6. VÉRIFICATION IMPORTANTE : Confirmer que l'import Xray a réussi (vérifier le contexte xray_context).
                
                Si tout est bon, valider le résultat. Le rapport final doit inclure une section "Résultat de l'Exécution Technique". Sinon, lister les corrections nécessaires.
            """),
            agent=agent,
            context=[code_context, design_context, xray_context],
            expected_output="Un rapport de validation final confirmant la qualité du code, le statut de l'exécution automatique (PASS/FAIL) et la réussite de l'import Xray."
        )

    def xray_push_task(self, agent, design_context, jira_context=None, project_key=None):
        description = dedent(f"""
            Utiliser l'outil 'import_gherkin_to_xray' pour envoyer les scénarios Gherkin validés lors du design dans Xray.
            
            INSTRUCTIONS:
            1. Extraire le contenu Gherkin provenant du design_context.
            2. Déterminer la clé du projet (Project Key) :
               - Priorité 1 : Utiliser la clé explicitement fournie : {project_key if project_key else "Non fournie"}.
               - Priorité 2 : Si non fournie, l'extraire du contexte Jira (jira_context).
            3. Appeler l'outil 'import_gherkin_to_xray' avec le contenu Gherkin et la clé du projet identifiée.
        """)
        
        context = [design_context]
        if jira_context:
            context.append(jira_context)
            
        return Task(
            description=description,
            agent=agent,
            context=context,
            expected_output="Une confirmation de l'import réussi dans Xray avec l'ID du test créé."
        )
