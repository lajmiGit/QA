import os
import argparse
from crewai import Crew, Process
from src.agents import LaboQaAgents
from src.tasks import LaboQaTasks
from src.tools.jira_tool import JiraIssueTool
from src.tools.xray_tool import XrayImportTool
from src.utils.file_manager import FileManager
from src.models import CodeGenerationOutput
import subprocess
import sys
import time
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Logger(object):
    def __init__(self, filename="output/execution.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        # Cette méthode est nécessaire pour la compatibilité avec sys.stdout
        pass

def run():
    # 0. Configuration du Logging
    if not os.path.exists("output"):
        os.makedirs("output")
    
    sys.stdout = Logger("output/execution.log")
    
    # Configuration des arguments de ligne de commande
    parser = argparse.ArgumentParser(description="Lancer le Labo QA IA autonome")
    parser.add_argument("--issue", type=str, help="Clé du ticket Jira (ex: QA-123)")
    parser.add_argument("--project", type=str, help="Clé du projet Jira/Xray (ex: SCRUM)")
    args = parser.parse_args()

    print("\n## Bienvenue au Labo QA IA - Initialisation du Crew ##")
    print("-----------------------------------------------------")

    # 1. Instanciation des Agents et Tâches
    agents_factory = LaboQaAgents()
    tasks_factory = LaboQaTasks()

    # Définition des agents
    analyst = agents_factory.analyst_agent()
    designer = agents_factory.designer_agent()
    sdet = agents_factory.sdet_agent()
    supervisor = agents_factory.supervisor_agent()
    integration = agents_factory.integration_agent()

    # 2. Détermination de la donnée d'entrée (Jira ID ou US par défaut)
    # This section is now handled within the task definition logic below.

    # 3. Définition des Tâches avec contexte
    active_tasks = []
    
    if args.issue:
        print(f"Option sélectionnée : Récupération dynamique du ticket Jira : {args.issue}")
        tsk_fetch = tasks_factory.jira_fetch_task(integration, args.issue)
        active_tasks.append(tsk_fetch)
        tsk_analysis = tasks_factory.analysis_task(analyst, user_story_context=tsk_fetch)
    else:
        # Valeur par défaut pour test local
        input_data = """
        Titre: US01 - Recherche de produit
        
        En tant que client du site Juice Shop,
        Je veux pouvoir rechercher des produits via la barre de recherche,
        Afin de trouver rapidement les articles que je souhaite acheter.
        
        Règles de gestion:
        - La recherche doit s'effectuer dès que l'utilisateur tape plus de 3 caractères ou appuie sur Entrée.
        - La recherche doit être insensible à la casse.
        - Les résultats doivent s'afficher dynamiquement.
        - Si aucun produit n'est trouvé, un message "No results found" doit s'afficher.
        - L'API appelée est /rest/products/search?q={keyword}.
        """
        print("Option sélectionnée : Utilisation de la User Story d'exemple (US01)")
        tsk_analysis = tasks_factory.analysis_task(analyst, direct_input=input_data)

    tsk_design = tasks_factory.test_design_task(designer, tsk_analysis)
    
    # On passe le contexte Jira (si existant) et éventuellement la clé projet forcée
    tsk_fetch = active_tasks[0] if args.issue else None
    
    # 3. L'import Xray se fait juste après le Design
    tsk_push = tasks_factory.xray_push_task(
        integration, 
        tsk_design, 
        jira_context=tsk_fetch,
        project_key=args.project
    )
    
    # 4. Le code est généré après (ou en parallèle, mais ici séquentiel)
    # On passe le contexte Xray (tsk_push) pour l'annotation des IDs
    tsk_code = tasks_factory.code_generation_task(sdet, tsk_design, tsk_push, issue_key=args.issue)
    
    # 5. La revue valide TOUT (Code + Résultat Xray)
    tsk_review = tasks_factory.review_task(supervisor, tsk_code, tsk_design, tsk_push)

    active_tasks.extend([tsk_analysis, tsk_design, tsk_push, tsk_code, tsk_review])

    # Ajouter une pause entre chaque tâche pour éviter le quota API Google
    def wait_next_task(output):
        print("\n[PAUSE] Attente de 30 secondes pour préserver le quota API... \n")
        time.sleep(30)

    for task in active_tasks:
        task.callback = wait_next_task

    # 4. Création du Crew
    crew = Crew(
        agents=[analyst, designer, sdet, supervisor, integration],
        tasks=active_tasks,
        verbose=True,
        process=Process.sequential
    )

    # 5. Lancement
    print("\nLancement du cycle de travail autonome...\n")
    result = crew.kickoff()
    
    # --- PHASE AUTOMATION : Écriture des fichiers et Exécution ---
    print("\n\n" + "="*50)
    print("🤖 PHASE AUTOMATION (FILE MANAGER & PLAYWRIGHT)")
    print("="*50)

    try:
        # Récupération de la sortie structurée du SDET
        # On suppose que tsk_code est la tâche de génération de code
        # CrewAI peuple task.output.pydantic si output_pydantic est utilisé
        
        sdet_output = tsk_code.output.pydantic
        
        if sdet_output and isinstance(sdet_output, CodeGenerationOutput):
            print(f"📝 Récupération de {len(sdet_output.files)} fichiers générés...")
            
            # Initialisation du FileManager pointant vers le dossier 'automation'
            file_manager = FileManager(base_path="./automation")
            created_files = file_manager.write_files(sdet_output.files)
            
            print(f"✅ Fichiers écrits avec succès : {created_files}")
            
            # Lancement des tests
            print("\n🚀 Lancement de l'exécution Playwright BDD...")
            # On vérifie d'abord que le dossier automation contient un package.json
            if os.path.exists("./automation/package.json"):
                # Etape 1: Génération des specs BDD
                print("   [1/2] Génération des specs (bddgen)...")
                bdd_cmd = ["npx", "bddgen"]
                bdd_process = subprocess.run(
                    bdd_cmd,
                    cwd="./automation",
                    capture_output=True,
                    text=True
                )
                if bdd_process.returncode != 0:
                    print("❌ Erreur bddgen :")
                    print(bdd_process.stderr)
                else:
                    print("   ✅ Specs générées.")

                # Etape 2: Exécution des tests
                print("   [2/2] Exécution des tests...")
                npm_cmd = ["npx", "playwright", "test"]
                process = subprocess.run(
                    npm_cmd,
                    cwd="./automation",
                    capture_output=True,
                    text=True
                )
                
                print("\n--- RÉSULTAT PLAYWRIGHT ---")
                print(process.stdout)
                if process.stderr:
                    print("[STDERR]")
                    print(process.stderr)
                
                if process.returncode == 0:
                    print("\n✅ TOUS LES TESTS SONT PASSÉS !")
                else:
                    print(f"\n❌ ECHEC DES TESTS (Code {process.returncode})")
            else:
                print("⚠️ Impossible de lancer les tests : Dossier 'automation' non initialisé.")
        else:
            print("⚠️ Pas de sortie structurée détectée pour la tâche de code.")
            # Fallback si pas de format pydantic (ex: ancienne version ou erreur agent)
            
    except Exception as e:
        print(f"❌ Erreur lors de la phase automation : {str(e)}")

    print("\n\n########################")
    print("## Resultat Global")
    print("########################\n")
    print(result)
    # 6. Sauvegarde du résultat
    if not os.path.exists("output"):
        os.makedirs("output")
        
    filename = f"output/result_{args.issue}.md" if args.issue else "output/final_result.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(str(result))

    print(f"\n-----------------------------------------------------")
    print(f"Travail terminé ! Résultats sauvegardés dans : {filename}")

if __name__ == "__main__":
    run()
