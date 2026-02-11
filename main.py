import os
import argparse
from crewai import Crew, Process
from src.agents import LaboQaAgents
from src.tasks import LaboQaTasks
from src.tools.jira_tool import JiraIssueTool
from src.tools.xray_tool import XrayImportTool

import sys
import time
from dotenv import load_dotenv
from src.utils.gemini_cache import context_manager

# Charger les variables d'environnement
# Charger les variables d'environnement
load_dotenv()
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"

class Logger(object):
    def __init__(self, filename="output/execution.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.terminal.flush() # Assurer la visibilité immédiate
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

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

    # 0.1 Initialisation du Cache Global (Context Caching Double)
    context_manager.initialize_all_caches()

    print("\n## Bienvenue au Labo QA IA - Initialisation du Crew ##")
    print("-----------------------------------------------------")

    # 1. Instanciation des Agents et Tâches
    agents_factory = LaboQaAgents()
    tasks_factory = LaboQaTasks()

    # Définition des agents
    analyst = agents_factory.analyst_agent()
    req_interviewer = agents_factory.requirement_interviewer_agent()
    designer = agents_factory.designer_agent()
    des_interviewer = agents_factory.design_interviewer_agent()
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
        tsk_analysis_draft = tasks_factory.analysis_task(analyst, user_story_context=tsk_fetch)
    else:
        # Valeur par défaut pour test local (Parabank)
        input_data = """
        Titre: SCRUM-273 Transfer Funds Feature
        
        Description:
        En tant qu'utilisateur connecté, je veux pouvoir transférer des fonds entre mes comptes.

        Critères d'Acceptation:
        1. Le lien "Transfer Funds" doit être accessible depuis le menu de gauche.
        2. Le formulaire de transfert (/parabank/transfer.htm) doit afficher:
           - Un champ Montant ($)
           - Une liste déroulante "From Account"
           - Une liste déroulante "To Account"
           - Un bouton "Transfer"
        3. Après validation, un message "Transfer Complete!" doit s'afficher.
        4. Le système doit afficher le montant transféré dans le message de confirmation.

        Note Technique:
        - L'utilisateur doit être connecté (john/demo).
        - URL cible: /parabank/transfer.htm
        """
        print("Option sélectionnée : Utilisation de la User Story d'exemple Parabank")
        tsk_analysis_draft = tasks_factory.analysis_task(analyst, direct_input=input_data)

    # 3. INTERVIEW ANALYSE (POINT PAR POINT)
    tsk_interview_analysis = tasks_factory.interview_analysis_task(req_interviewer, tsk_analysis_draft)

    # 4. DESIGN (BROUILLON AVEC SCENARIO OUTLINES)
    tsk_design_draft = tasks_factory.test_design_task(designer, tsk_interview_analysis)
    
    # 5. INTERVIEW DESIGN (JDD DANS LES EXAMPLES)
    tsk_interview_design = tasks_factory.interview_design_task(des_interviewer, tsk_design_draft)
    
    # 6. XRAY PUSH
    tsk_fetch_context = active_tasks[0] if args.issue else None
    tsk_push = tasks_factory.xray_push_task(
        integration, 
        tsk_interview_design, 
        jira_context=tsk_fetch_context,
        project_key=args.project
    )
    
    # 7. CODE GENERATION
    base_url = os.getenv("BASE_URL")
    tsk_code = tasks_factory.code_generation_task(sdet, tsk_interview_design, tsk_push, issue_key=args.issue, base_url=base_url)
    
    # 8. SUPERVISOR REVIEW
    tsk_review = tasks_factory.review_task(supervisor, tsk_code, tsk_interview_design, tsk_push)

    active_tasks.extend([tsk_analysis_draft, tsk_interview_analysis, tsk_design_draft, tsk_interview_design, tsk_push, tsk_code, tsk_review])

    # Ajouter une pause entre chaque tâche pour éviter le quota API Google
    def wait_next_task(output):
        print("\n[PAUSE] Attente de 20 secondes pour préserver le quota API (Test Mode)... \n")
        time.sleep(20)

    for task in active_tasks:
        task.callback = wait_next_task

    # 4. Création du Crew
    crew = Crew(
        agents=[analyst, req_interviewer, designer, des_interviewer, sdet, supervisor, integration],
        tasks=active_tasks,
        verbose=True,
        process=Process.sequential
    )

    # 5. Lancement
    print("\nLancement du cycle de travail autonome...\n")
    try:
        result = crew.kickoff()
    finally:
        # Nettoyage automatique du cache à la fin, même en cas de crash
        context_manager.cleanup()
    
    # --- PHASE AUTOMATION : Gérée par le SDET autonome via MCP ---
    print("\n\n" + "="*50)
    print("🤖 PHASE AUTOMATION (AUTONOMOUS AGENT)")
    print("="*50)
    print("Le SDET a directement interagi avec le système via MCP.")
    print("Vérifiez le rapport final ci-dessus pour les détails.")

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
