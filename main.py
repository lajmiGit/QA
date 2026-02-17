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
from src.connectors import get_connector

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

    def fileno(self):
        return self.terminal.fileno()

def run():
    # 0. Configuration du Logging
    if not os.path.exists("output"):
        os.makedirs("output")
    
    logger = Logger("output/execution.log")
    sys.stdout = logger
    sys.stderr = logger
    
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

    # 2. Récupération de la donnée d'entrée via Connecteurs Directs (Haute Performance)
    user_story_content = ""
    if args.issue:
        print(f"🚀 Récupération directe du ticket Jira : {args.issue}...")
        connector = get_connector("jira")
        user_story_content = connector.fetch(args.issue)
    else:
        # Valeur par défaut pour test local (Parabank) ou input direct
        print("🚀 Utilisation de la source par défaut (Text/Local)...")
        default_input = """
        Titre: SCRUM-273 Transfer Funds Feature
        Description: En tant qu'utilisateur connecté, je veux pouvoir transférer des fonds entre mes comptes.
        URL cible: /parabank/transfer.htm
        """
        connector = get_connector("text")
        user_story_content = connector.fetch(default_input)

    print("✅ Données récupérées avec succès.")

    # 3. Définition des Tâches
    # On passe directement le contenu récupéré à l'analyse
    tsk_analysis_draft = tasks_factory.analysis_task(analyst, direct_input=user_story_content)

    # 3. INTERVIEW ANALYSE (POINT PAR POINT)
    tsk_interview_analysis = tasks_factory.interview_analysis_task(req_interviewer, tsk_analysis_draft)

    # 2. DESIGN (BROUILLON AVEC SCENARIO OUTLINES)
    tsk_design_draft = tasks_factory.test_design_task(designer, tsk_interview_analysis)
    
    # 3. INTERVIEW DESIGN (JDD DANS LES EXAMPLES)
    tsk_interview_design = tasks_factory.interview_design_task(des_interviewer, tsk_design_draft)
    
    # 4. XRAY PUSH
    tsk_push = tasks_factory.xray_push_task(
        integration, 
        tsk_interview_design, 
        project_key=args.project
    )
    
    # 7. CODE GENERATION
    # OPTIMISATION CONTEXT PRUNING :
    # On ne passe QUE le design validé (Pydantic) et le résultat du push (pour l'ID Xray).
    # On coupe le lien avec l'analyse et les vidéos pour éviter l'effet "Sac à dos".
    base_url = os.getenv("BASE_URL")
    tsk_code = tasks_factory.code_generation_task(
        sdet, 
        design_context=tsk_design_draft, # Contient l'objet GherkinDesign propre
        xray_context=tsk_push,           # Contient l'ID du test créé
        issue_key=args.issue, 
        base_url=base_url
    )
    
    # 8. SUPERVISOR REVIEW
    tsk_review = tasks_factory.review_task(supervisor, tsk_code, tsk_design_draft, tsk_push)

    # 4. Création de la liste des tâches (active_tasks)
    active_tasks = [tsk_analysis_draft, tsk_interview_analysis, tsk_design_draft, tsk_interview_design, tsk_push, tsk_code, tsk_review]

    # 4. Création du Crew (SANS MÉMOIRE GLOBALE POUR ÉVITER LE SAC À DOS)
    crew = Crew(
        agents=[analyst, req_interviewer, designer, des_interviewer, sdet, supervisor, integration],
        tasks=active_tasks,
        verbose=True,
        process=Process.sequential,
        memory=False # <--- STOP LEAK : On force l'oubli entre les tâches non liées
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
