from crewai import Agent, Task, Crew, Process, LLM
import os
from dotenv import load_dotenv

load_dotenv()

try:
    print("Testing CrewAI memory=False support...")
    
    # Dummy agent
    agent = Agent(
        role='Tester',
        goal='Just say hello',
        backstory='You are a test agent',
        verbose=True,
        allow_delegation=False,
        llm=MockLLM()
    )
    
    # Dummy task
    task = Task(
        description='Say hello',
        agent=agent,
        expected_output='Hello world'
    )
    
    # Crew with memory=False
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True,
        process=Process.sequential,
        memory=False
    )
    
    print("Crew initialized successfully with memory=False")

    # Try kicking off
    crew.kickoff()
    print("Kickoff success")
    
except TypeError as e:
    print(f"CRITICAL ERROR (TypeError): {e}")
except Exception as e:
    print(f"ERROR: {e}")
