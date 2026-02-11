# Schéma du Workflow des Agents et Tâches

Ce schéma illustre le cycle de vie complet d'une User Story, de sa récupération dans Jira jusqu'à sa validation finale et son automatisation.

```mermaid
graph TD
    subgraph "Phase d'Initialisation"
        Jira[("Ticket Jira (Issue)")] --> IntAgent["Agent d'Intégration"]
        IntAgent -- "fetch_jira_task" --> US_Brute["User Story Brute"]
    end

    subgraph "Phase d'Analyse & Validation"
        US_Brute --> Analyst["Analyste QA (Flash)"]
        Analyst <--> User_Res{{"Utilisateur (Sélection Dossier - ask_human)"}}
        Analyst -- "analysis_task" --> Draft_Rules["Brouillon des Règles"]
        Draft_Rules --> ReqInter["Requirement Interviewer"]
        
        ReqInter <--> User_V1{{"Utilisateur (ask_human)"}}
        ReqInter <--> KB_Q1[("Memory (query)")]
        ReqInter -- "Mémorisation" --> KB_U1[("Memory (update)")]
        
        ReqInter -- "interview_analysis_task" --> Valid_Rules["Règles Validées"]
    end

    subgraph "Phase de Design & JDD"
        Valid_Rules --> Designer["Designer BDD"]
        Designer -- "test_design_task" --> Draft_Gherkin["Brouillon Gherkin"]
        
        Draft_Gherkin --> DesInter["Design Interviewer"]
        
        DesInter <--> User_V2{{"Utilisateur (ask_human)"}}
        DesInter <--> KB_Q2[("Memory (query)")]
        
        User_V2 -- "Validation 'GO'" --> Final_Auth["Autorisation Finale"]
        Final_Auth -- "Mémorisation" --> KB_U2[("Memory (update)")]
    end

    subgraph "Phase technique & Export"
        Final_Auth --> IntAgent2["Agent d'Intégration"]
        IntAgent2 -- "xray_push_task" --> Xray[("Xray Cloud")]
        
        Final_Auth --> SDET["Ingénieur SDET"]
        SDET <--> MCP[("Serveur MCP (Exploration & Test)")]
        SDET -- "code_generation_task" --> Code["Playwright Code (POM)"]
    end

    subgraph "Phase de Clôture"
        Code & Xray --> Supervisor["Superviseur (QA Lead)"]
        Supervisor -- "review_task" --> Final_Report["Rapport Final / Wiki"]
    end

    style User_V1 fill:#f9f,stroke:#333,stroke-width:2px
    style User_V2 fill:#f9f,stroke:#333,stroke-width:2px
    style Final_Auth fill:#0f0,stroke:#333,stroke-width:4px
```

## Légende
- **Rectangles** : Agents CrewAI.
- **Flèches avec texte** : Tâches (`Task`) spécifiques.
- **Formes violettes** : Points d'interaction humaine (`ask_human`).
- **Formes vertes** : Porte de validation critique ("GO" Gate).
- **Cylindres** : Stockage de données (Jira, Xray, Memory).
