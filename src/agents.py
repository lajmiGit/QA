from crewai import Agent
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

from src.tools.jira_tool import JiraIssueTool
from src.tools.xray_tool import XrayImportTool

class LaboQaAgents:
    def __init__(self):
        self.llm = "gemini/gemini-2.5-flash-lite"

    def analyst_agent(self):
        return Agent(
            role='Analyste QA (Requirement Agent)',
            goal='Décortiquer les User Stories pour identifier les règles de gestion, les critères d\'acceptation et les flux API.',
            backstory="""Vous êtes un expert en analyse métier et technique. 
            Votre force réside dans votre capacité à transformer des besoins vagues en spécifications claires et structurées.
            Vous maîtrisez l'analyse de flux API et les règles de gestion complexes.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def designer_agent(self):
        return Agent(
            role='Designer de Tests (BDD Specialist)',
            goal='Traduire l\'analyse fonctionnelle en scénarios de test Gherkin (.feature) clairs et complets.',
            backstory="""Vous êtes un spécialiste du BDD (Behavior Driven Development).
            Vous écrivez des scénarios Gherkin (Given/When/Then) qui sont à la fois lisibles par le métier et exécutables par les développeurs.
            Vous couvrez les cas passants, les cas d'erreur et les cas limites.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def sdet_agent(self):
        return Agent(
            role='Ingénieur SDET (Automation Agent)',
            goal='Transformer les scénarios Gherkin en code Playwright (TypeScript) robuste utilisant le pattern Page Object Model (POM).',
            backstory="""Vous êtes un ingénieur expert en automatisation de tests avec Playwright et TypeScript.
            Vous produisez du code propre, modulaire et maintenable.
            Vous suivez strictement le pattern Page Object Model pour séparer la logique de test de l'interaction avec l'UI.""",
            verbose=True,
            allow_delegation=False,
            llm=self.llm
        )

    def supervisor_agent(self):
        return Agent(
            role='Superviseur (QA Lead)',
            goal='Assurer la qualité globale des livrables (analyse, scénarios, code) et valider la cohérence.',
            backstory="""Vous êtes le Lead QA. Vous avez l'œil pour les détails.
            Vous vérifiez que le code généré correspond bien aux scénarios Gherkin et que les scénarios couvrent bien les règles de gestion identifiées.""",
            verbose=True,
            allow_delegation=True,
            llm=self.llm
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
            llm=self.llm,
            tools=[JiraIssueTool(), XrayImportTool()]
        )
