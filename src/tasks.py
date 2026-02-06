from crewai import Task
from textwrap import dedent

class LaboQaTasks:
    def jira_fetch_task(self, agent, issue_key):
        return Task(
            description=dedent(f"""
                Utiliser l'outil 'fetch_jira_issue' pour récupérer le contenu complet de l'issue Jira: {issue_key}.
                Extraire le titre, la description et tous les détails pertinents.
            """),
            agent=agent,
            expected_output="Le contenu brut de la User Story récupéré depuis Jira."
        )

    def analysis_task(self, agent, user_story_context=None, direct_input=None):
        description = "Analyser la User Story pour en extraire toutes les informations nécessaires aux tests.\n\n"
        if direct_input:
            description += f"Donnée d'entrée directe: {direct_input}\n"
        
        description += dedent("""
            INSTRUCTIONS:
            1. Analyser le contenu fourni (soit via le contexte Jira, soit via l'entrée directe).
            2. Identifiez les règles de gestion détaillées.
            3. Listez les critères d'acceptation.
            4. Analysez les flux API mentionnés ou nécessaires.
            
            Détails attendus:
            1. Règles de gestion explicites et implicites.
            2. Critères d'acceptation.
            3. Flux de données et appels API potentiels.
            4. Données de test requises.
        """)
        
        context = [user_story_context] if user_story_context else []
        
        return Task(
            description=description,
            agent=agent,
            context=context,
            expected_output="Un document d'analyse détaillé structuré en sections (Règles, Critères, API, Données)."
        )

    def test_design_task(self, agent, analysis_context, issue_key=None):
        return Task(
            description=dedent(f"""
                À partir de l'analyse fournie, générer les scénarios de test au format Gherkin (.feature).
                
                CONSIGNES:
                1. Créer un fichier Gherkin complet avec Feature, Background (si pertinent) et Scenarios.
                2. Couvrir les cas nominaux (Happy Path).
                3. Couvrir les cas d'erreurs et les cas limites (Edge Cases).
                4. Utiliser l'anglais pour le Gherkin (plus standard pour l'automatisation).
                
                Format de sortie attendu: Contenu d'un fichier .feature uniquement.
            """),
            agent=agent,
            context=[analysis_context],
            expected_output="Le contenu complet d'un fichier .feature."
        )

    def code_generation_task(self, agent, design_context, xray_context, issue_key=None):
        feature_tag_instruction = ""
        if issue_key:
            feature_tag_instruction = f"- Tu dois insérer le tag de la User Story (@{issue_key}) juste au dessus de 'Feature:'."
            
        from src.models import CodeGenerationOutput

        return Task(
            description=dedent(f"""
                Traduire les scénarios Gherkin en Step Definitions Playwright (BDD).
                
                EXIGENCES:
                1. Utiliser le pattern Page Object Model (POM).
                2. Écrire en TypeScript.
                3. Utiliser `createBdd` de `playwright-bdd` pour les steps.
                4. Séparer le Page Object (.page.ts) des Step Definitions (.steps.ts).
                
                INTEGRATION XRAY :
                Conserver les tags Xray dans le fichier `.feature` (via la réécriture), cela suffit pour la traçabilité.
                   
                LIVRABLES ATTENDUS :
                Tu dois fournir une liste de fichiers structurée (JSON/Pydantic).
                
                Liste des fichiers attendus :
                1. `features/<feature>.feature` (Le Gherkin enrichi avec les tags @SCRUM-XXX)
                2. `src/pages/<feature>.page.ts` (Page Object standard Playwright)
                3. `steps/<feature>.steps.ts` (Step Definitions)
                
                Exemple de Step Definition :
                ```typescript
                import {{ createBdd }} from 'playwright-bdd';
                import {{ test }} from './fixtures'; // ou import standard
                import {{ MyPage }} from '../src/pages/my.page';

                const {{ Given, When, Then }} = createBdd();

                // IMPORTANT : N'utilisez JAMAIS 'And' ou 'But' en TypeScript.
                // Mappez les étapes 'And' d'un Feature vers Given/When/Then selon le contexte.

                Given('I am on the homepage', async ({{ page }}) => {{
                    const myPage = new MyPage(page);
                    await myPage.goto();
                }});
                ```
            """),
            agent=agent,
            context=[design_context, xray_context],
            output_pydantic=CodeGenerationOutput,
            expected_output="Un objet CodeGenerationOutput contenant les fichiers .feature, .page.ts et .steps.ts."
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
                5. VÉRIFICATION IMPORTANTE : Confirmer que l'import Xray a réussi (vérifier le contexte xray_context).
                
                Si tout est bon, valider le résultat. Sinon, lister les corrections nécessaires.
            """),
            agent=agent,
            context=[code_context, design_context, xray_context],
            expected_output="Un rapport de validation final confirmant la qualité du code et la réussite de l'import Xray."
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
