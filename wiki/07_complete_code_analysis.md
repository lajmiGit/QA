# Analyse Complète du Code Source

Ce document regroupe l'intégralité du code source du projet Labo QA IA avec des explications détaillées pour chaque fichier et chaque bloc logique.

---

## 1. `src/agents.py` : Les Cerveaux

Ce fichier définit les agents IA qui vont réaliser le travail.

```python
from crewai import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv

# 1. Chargement de la configuration
# On charge les variables d'environnement (comme la clé API) depuis le fichier .env
load_dotenv()

# 2. Configuration du modèle d'IA (LLM)
# On initialise le connecteur vers Google Gemini.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",    # Modèle rapide et efficace
    verbose=True,                # Affiche les détails d'exécution
    temperature=0.2,             # Faible créativité (= haute précision pour le code)
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# 3. Définition des Agents
class LaboQaAgents:
    
    # --- Agent Analyste ---
    def analyst_agent(self):
        return Agent(
            role='Analyste QA (Requirement Agent)',
            # Goal: L'objectif précis que l'agent doit atteindre
            goal='Décortiquer les User Stories pour identifier les règles de gestion, les critères d\'acceptation et les flux API.',
            # Backstory: Donne le contexte et l'expertise à l'agent
            backstory="""Vous êtes un expert en analyse métier et technique. 
            Votre force réside dans votre capacité à transformer des besoins vagues en spécifications claires et structurées.
            Vous maîtrisez l'analyse de flux API et les règles de gestion complexes.""",
            verbose=True,
            allow_delegation=False, # L'agent travaille seul
            llm=llm
        )

    # --- Agent Designer ---
    def designer_agent(self):
        return Agent(
            role='Designer de Tests (BDD Specialist)',
            goal='Traduire l\'analyse fonctionnelle en scénarios de test Gherkin (.feature) clairs et complets.',
            # On insiste sur le format Gherkin (Given/When/Then)
            backstory="""Vous êtes un spécialiste du BDD (Behavior Driven Development).
            Vous écrivez des scénarios Gherkin (Given/When/Then) qui sont à la fois lisibles par le métier et exécutables par les développeurs.
            Vous couvrez les cas passants, les cas d'erreur et les cas limites.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    # --- Agent SDET (Développeur de Test) ---
    def sdet_agent(self):
        return Agent(
            role='Ingénieur SDET (Automation Agent)',
            goal='Transformer les scénarios Gherkin en code Playwright (TypeScript) robuste utilisant le pattern Page Object Model (POM).',
            # On impose l'architecture logicielle (Page Object Model)
            backstory="""Vous êtes un ingénieur expert en automatisation de tests avec Playwright et TypeScript.
            Vous produisez du code propre, modulaire et maintenable.
            Vous suivez strictement le pattern Page Object Model pour séparer la logique de test de l'interaction avec l'UI.""",
            verbose=True,
            allow_delegation=False,
            llm=llm
        )

    # --- Agent Superviseur ---
    def supervisor_agent(self):
        return Agent(
            role='Superviseur (QA Lead)',
            goal='Assurer la qualité globale des livrables (analyse, scénarios, code) et valider la cohérence.',
            # Rôle de validation et de contrôle qualité
            backstory="""Vous êtes le Lead QA. Vous avez l'œil pour les détails.
            Vous vérifiez que le code généré correspond bien aux scénarios Gherkin et que les scénarios couvrent bien les règles de gestion identifiées.
            Vous garantissez que le projet respecte les standards de qualité.""",
            verbose=True,
            allow_delegation=True, # Autorisé à déléguer (théoriquement)
            llm=llm
        )
```

---

## 2. `src/tasks.py` : Les Missions

Ce fichier définit les tâches précises que chaque agent doit accomplir.

```python
from crewai import Task
from textwrap import dedent # Permet d'écrire des strings multi-lignes sans indentation gênante

class LaboQaTasks:

    # --- Tâche 1 : Analyse ---
    def analysis_task(self, agent, user_story):
        return Task(
            # Description détaillée de ce qu'il faut faire avec l'input (user_story)
            description=dedent(f"""
                Analyser la User Story suivante pour en extraire toutes les informations nécessaires aux tests.
                
                User Story:
                {user_story}
                
                Détails attendus:
                1. Règles de gestion explicites et implicites.
                2. Critères d'acceptation.
                3. Flux de données et appels API potentiels.
                4. Données de test requises.
            """),
            agent=agent, # L'agent assigné (Analyste)
            expected_output="Un document d'analyse complet listant les règles de gestion, critères d'acceptation et scénarios identifiés."
        )

    # --- Tâche 2 : Design de Test ---
    def test_design_task(self, agent, analysis_context):
        return Task(
            description=dedent(f"""
                Sur la base de l'analyse fournie, rédigez les scénarios de test au format Gherkin (Cucumber).
                
                Le contexte d'analyse est le suivant:
                (Le résultat de la tâche précédente sera utilisé ici automatiquement par CrewAI si passé en contexte)
                
                Exigences:
                1. Utiliser le format Given / When / Then.
                2. Couvrir les cas nominaux ("Happy Path").
                3. Couvrir les cas d'erreur ("Edge cases").
                4. Utiliser l'anglais pour le Gherkin (plus standard pour l'automatisation).
                
                Format de sortie attendu: Contenu d'un fichier .feature.
            """),
            agent=agent, # L'agent assigné (Designer)
            context=[analysis_context], # <--- IMPORTANT: On passe le résultat de l'analyse en entrée
            expected_output="Un ensemble de scénarios au format Gherkin (.feature) prêts à être implémentés."
        )

    # --- Tâche 3 : Génération de Code ---
    def code_generation_task(self, agent, design_context):
        return Task(
            description=dedent(f"""
                Générer le code d'automatisation Playwright (TypeScript) pour les scénarios Gherkin fournis.
                
                Exigences Techniques:
                1. Utiliser le pattern Page Object Model (POM).
                2. Créer une classe de Page Object par page/composant majeur.
                3. Créer un fichier de test (.spec.ts) qui utilise ces Page Objects.
                4. Le code doit être complet, importable et syntaxiquement correct.
                5. Inclure les commentaires nécessaires.
                
                Format de sortie: Code TypeScript complet pour les Page Objects et les Specs. Indiquer clairement les noms de fichiers suggérés.
            """),
            agent=agent, # L'agent assigné (SDET)
            context=[design_context], # On passe les scénarios Gherkin en entrée
            expected_output="Le code source TypeScript complet (Page Objects + Tests) implémentant les scénarios Gherkin."
        )

    # --- Tâche 4 : Revue de Code ---
    def review_task(self, agent, code_context):
        return Task(
            description=dedent(f"""
                Revoir le code généré et les scénarios de test pour assurer la qualité.
                
                Vérifications:
                1. Le code Playwright semble-t-il valide et complet ?
                2. Les sélecteurs utilisés semblent-ils robustes ?
                3. Le code respecte-t-il le pattern POM ?
                4. Tous les scénarios Gherkin sont-ils couverts par le code ?
                
                Si tout est bon, valider le résultat. Sinon, lister les corrections nécessaires.
            """),
            agent=agent, # L'agent assigné (Superviseur)
            context=[code_context], # On passe le code généré en entrée
            expected_output="Un rapport de validation confirmant la qualité du code ou listant les améliorations requises."
        )
```

---

## 3. `main.py` : Le Chef d'Orchestre

Ce fichier assemble le tout et lance l'exécution.

```python
import os
from crewai import Crew, Process
from src.agents import LaboQaAgents
from src.tasks import LaboQaTasks
from dotenv import load_dotenv

# 1. Chargement des variables d'environnement
load_dotenv()

def run():
    print("## Bienvenue au Labo QA IA - Initialisation du Crew ##")
    print("-----------------------------------------------------")

    # 2. Instanciation des Agents
    # On crée les "robots" prêts à travailler
    agents = LaboQaAgents()
    analyst = agents.analyst_agent()
    designer = agents.designer_agent()
    sdet = agents.sdet_agent()
    supervisor = agents.supervisor_agent()

    # 3. Définition de l'Input (User Story)
    # Dans un cas réel, cela pourrait venir d'un fichier externe
    us01_content = """
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

    # 4. Instanciation des Tâches
    # On assigne les missions aux agents
    tasks = LaboQaTasks()
    
    # On voit ici le flux de données se construire :
    # Tâche 1 prend l'US
    tsk_analysis = tasks.analysis_task(analyst, us01_content)
    
    # Tâche 2 prend le résultat de Tâche 1 (tsk_analysis)
    tsk_design = tasks.test_design_task(designer, tsk_analysis)
    
    # Tâche 3 prend le résultat de Tâche 2 (tsk_design)
    tsk_code = tasks.code_generation_task(sdet, tsk_design)
    
    # Tâche 4 prend le résultat de Tâche 3 (tsk_code)
    tsk_review = tasks.review_task(supervisor, tsk_code)

    # 5. Création du Crew (L'équipe au complet)
    crew = Crew(
        agents=[analyst, designer, sdet, supervisor],
        tasks=[tsk_analysis, tsk_design, tsk_code, tsk_review],
        verbose=True,  # Important pour suivre la réflexion des agents dans la console
        process=Process.sequential # Exécution séquentielle (l'un après l'autre)
    )

    # 6. Lancement
    print(f"Lancement du traitement pour l'US:\n{us01_content}\n")
    
    # kickoff() lance la machine !
    result = crew.kickoff()

    print("\n\n########################")
    print("## RÉSULTAT FINAL DU CREW ##")
    print("########################\n")
    print(result)

    # 7. Sauvegarde du résultat
    with open("output/final_result.md", "w") as f:
        f.write(str(result))

if __name__ == "__main__":
    run()
```
