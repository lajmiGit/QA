from crewai import Agent, LLM
import os
from src.config import MODEL_PRO, MAX_RPM_PRO, MAX_RPM_FLASH, MODEL_FLASH, MAX_RETRIES, TIMEOUT
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from src.tools.jira_tool import JiraIssueTool
from src.tools.xray_tool import XrayImportTool
from src.tools.playwright_mcp import WriteFileTool, ReadFileTool, RunPlaywrightTestTool, ListFilesTool, InspectPageTool, TakeScreenshotTool, GetConsoleLogsTool, ExplorePageTool
from src.tools.human_tool import HumanInputTool
from src.tools.knowledge_tool import QueryKnowledgeTool, UpdateKnowledgeTool
from src.tools.vision_tool import VisionResourceTool
from src.tools.video_tool import VideoResourceTool

class LaboQaAgents:
    def __init__(self):
        # Configuration LLM PRO (Raisonnement complexe)
        # Note: CrewAI utilise le format "provider/model"
        self.llm_pro = LLM(
            model=f"google/{MODEL_PRO}",
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_rpm=MAX_RPM_PRO
        )
        
        # Configuration LLM FLASH (Exploration et Tâches simples)
        self.llm_flash = LLM(
            model=f"google/{MODEL_FLASH}",
            api_key=os.getenv("GOOGLE_API_KEY"),
            max_rpm=MAX_RPM_FLASH
        )
        
        self.query_tool = QueryKnowledgeTool()
        self.update_tool = UpdateKnowledgeTool()

    def analyst_agent(self):
        return Agent(
            role='Analyste QA (Requirement Specialist)',
            goal='Analyser la User Story, explorer les ressources visuelles et produire un inventaire des règles.',
            backstory="""Vous êtes un expert en analyse QA. Votre rôle est d'extraire les règles métier.
            VOTRE RÈGLE D'OR : "Knowledge First". Avant toute chose, vous DEVEZ interroger le 'Cerveau du Projet' via `query_knowledge` en posant une question en langage naturel sur ce qui est déjà connu (ex: quelles sont les règles d'authentification ?).
            Vous EXPLOREZ systématiquement le dossier 'resources/' à la racine pour trouver des maquettes et des vidéos liées à la US.
            Vous utilisez les outils 'analyze_resource_image' et 'analyze_scenario_video' pour m'expliquer ce que vous voyez.
            Vous ne parlez pas directement à l'utilisateur ; vous produisez un brouillon technique consolidé avec l'existant.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_flash, # Passage en Flash pour économiser le quota Pro
            tools=[self.query_tool, VisionResourceTool(), VideoResourceTool(), ListFilesTool(), HumanInputTool()]
        )

    def designer_agent(self):
        return Agent(
            role='Designer de Tests (BDD Specialist)',
            goal='Concevoir des scénarios Gherkin utilisant des Scenario Outlines et des tables Examples pour les JDD.',
            backstory="""Vous êtes un expert BDD puriste. Vous transformez l'analyse en structures Gherkin 
            modernes. Vous utilisez IMPÉRATIVEMENT des 'Scenario Outline' avec des tables 'Examples' 
            pour intégrer les données de test de manière propre et réutilisable.
            Vous consultez la base de connaissances pour connaître les JDD préférés et les conventions de nommage.
            Vous produisez des brouillons techniques pour le Validateur de Design.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_pro, # Garde Pro pour la logique Gherkin fine
            tools=[self.query_tool]
        )

    def requirement_interviewer_agent(self):
        return Agent(
            role='Expert en Analyse de Besoins (Interview Lead)',
            goal='Valider et affiner les règles de gestion via un dialogue point par point.',
            backstory="""Vous êtes un facilitateur focalisé sur le périmètre métier. 
            Vous prenez les règles brutes de l'Analyste et menez l'interview pour obtenir un OK sur chaque règle.
            Vous utilisez la base de connaissances pour suggérer des réponses à l'utilisateur basées sur l'historique.
            Vous vulgarisez la technique pour l'utilisateur.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_flash, # Flash suffit pour le dialogue de validation
            tools=[HumanInputTool(), self.query_tool, self.update_tool, VisionResourceTool(), VideoResourceTool()]
        )

    def design_interviewer_agent(self):
        return Agent(
            role='Validateur de Design & JDD (Scenario Lead)',
            goal='Valider les scénarios Gherkin et les jeux de données (Examples) point par point.',
            backstory="""Vous êtes un expert en stratégie de test. Vous présentez chaque scénario et 
            chaque ligne de donnée (Examples) à l'utilisateur. 
            Vous utilisez la mémoire du projet pour proposer les JDD habituels.
            AVANT DE FINIR : Vous devez IMPÉRATIVEMENT présenter le fichier Gherkin complet 
            et attendre un 'GO' clair de l'utilisateur via `ask_human`.
            Il est strictement interdit de terminer votre mission sans cette autorisation finale.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_flash, # Flash suffit pour le dialogue de validation
            tools=[HumanInputTool(), self.query_tool, self.update_tool, VisionResourceTool(), VideoResourceTool()]
        )

    def sdet_agent(self):
        return Agent(
            role='Ingénieur SDET (Automation Agent)',
            goal='Transformer les scénarios Gherkin en code Playwright (TypeScript) robuste utilisant le pattern Page Object Model (POM).',
            backstory="""Vous êtes un ingénieur expert en automatisation avec Playwright et expert en diagnostic visuel assisté par IA.
            VOTRE RÈGLE D'OR : "Audit First, Code Second".
            Avant de créer un fichier, vous DEVEZ vérifier s'il existe déjà une page ou un test similaire.
            En cas d'échec de test, vous utilisez SYSTÉMATIQUEMENT vos capacités de VISION et VIDÉO pour confronter le code au rendu réel de la page.
            Vous savez que sur Firefox/Webkit, certains éléments comme les dropdowns demandent parfois `toBeAttached()` plutôt que `toBeVisible()`.
            Vous préférez la MODIFICATION et le REFACTORING de fichiers existants à la création de doublons."""
,
            verbose=True,
            allow_delegation=False,
            llm=self.llm_pro, # Garde Pro pour la génération de code critique
            tools=[WriteFileTool(), ReadFileTool(), RunPlaywrightTestTool(), ListFilesTool(), InspectPageTool(), TakeScreenshotTool(), GetConsoleLogsTool(), HumanInputTool(), ExplorePageTool(), VisionResourceTool(), VideoResourceTool()]
        )

    def supervisor_agent(self):
        return Agent(
            role='Superviseur (QA Lead)',
            goal='Assurer la qualité globale des livrables (analyse, scénarios, code) et valider la cohérence.',
            backstory="""Vous êtes le Lead QA. Vous avez l'œil pour les détails.
            Vous vérifiez que le code généré correspond bien aux scénarios Gherkin et que les scénarios couvrent bien les règles de gestion identifiées.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_pro # Garde Pro pour la supervision haute fidélité
        )

    def integration_agent(self):
        return Agent(
            role='Agent d\'Intégration (Jira/Xray Connector)',
            goal='Gérer toutes les interactions avec Jira et Xray.',
            backstory="""Vous êtes responsable de la communication avec les outils externes. 
            Vous extrayez les informations de Jira et publiez les résultats de tests dans Xray.
            Vous assurez que la liaison entre les tickets et les tests est maintenue.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm_flash, # Flash suffit pour le parsing Jira/Xray JSON
            tools=[JiraIssueTool(), XrayImportTool()]
        )
