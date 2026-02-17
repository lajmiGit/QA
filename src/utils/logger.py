from crewai.tasks.task_output import TaskOutput
from crewai.agents.parser import AgentAction

class StepLogger:
    def __init__(self, filename="output/gemini_requests.log"):
        self.filename = filename
        # On vide le fichier au démarrage
        with open(self.filename, "w", encoding="utf-8") as f:
            f.write("=== LOG DÉTAILLÉ DES REQUÊTES GEMINI ===\n\n")

    def log_step(self, step_output):
        """
        Callback fonction appelée après chaque étape d'un agent.
        Capture: Agent, Thought, Tool, Tool Input, Observatiion.
        """
        # Dans les versions récentes de CrewAI, step_output est un tuple ou un objet complexe
        # On essaie d'extraire les infos de manière générique
        
        try:
            # Structure typique d'un step_output dans CrewAI : (AgentAction, Observation)
            if isinstance(step_output, tuple) and len(step_output) >= 2:
                action = step_output[0]
                observation = step_output[1]
                
                if isinstance(action, AgentAction):
                    # Tentative d'extraction des tokens (CrewAI stocke parfois ça dans l'action ou le result)
                    token_info = ""
                    if hasattr(action, 'result') and hasattr(action.result, 'token_usage'):
                         usage = action.result.token_usage
                         token_info = f"\n💎 TOKENS     : Input: {usage.prompt_tokens} / Output: {usage.completion_tokens} / Total: {usage.total_tokens}"
                    
                    log_entry = f"""
--------------------------------------------------------------------------------
[AGENT] {action.tool} (Tool Call)
--------------------------------------------------------------------------------
🛠️  TOOL       : {action.tool}
📥  INPUT      : {action.tool_input}{token_info}
📋  LOG (Thought) : 
{action.log}

📤  OBSERVATION (Tool Output) :
{observation}
--------------------------------------------------------------------------------
"""
                    self._append_to_log(log_entry)
            else:
                 # Capture générique pour d'autres formats (ex: AgentFinish)
                 log_entry = f"""
--------------------------------------------------------------------------------
[UNKNOWN STEP FORMAT]
--------------------------------------------------------------------------------
{str(step_output)}
--------------------------------------------------------------------------------
"""
                 self._append_to_log(log_entry)


        except Exception as e:
            self._append_to_log(f"\n[LOGGER ERROR]: {str(e)}\n")

    def _append_to_log(self, content):
        with open(self.filename, "a", encoding="utf-8") as f:
            f.write(content + "\n")

# Instance globale
step_logger = StepLogger()
