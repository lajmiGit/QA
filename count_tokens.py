import tiktoken
import re

def analyze_requests(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()

        requests = re.split(r'\n(?=\[AGENT\]|\[UNKNOWN STEP FORMAT\])', content)
        encoding = tiktoken.get_encoding("cl100k_base")
        
        print(f"{'TYPE / TOOL':<40} | {'TOKENS':<10} | {'PREVIEW':<30}")
        print("-" * 90)

        total_tokens = 0
        
        for req in requests:
            req = req.strip()
            if not req or req == "=== LOG DÉTAILLÉ DES REQUÊTES GEMINI ===":
                continue
                
            # Identifier le type
            name = "Unknown"
            if "[AGENT]" in req:
                tool_match = re.search(r'\[AGENT\] (.*?) \(Tool Call\)', req)
                name = tool_match.group(1).strip() if tool_match else "Agent Action"
            elif "[UNKNOWN STEP FORMAT]" in req:
                name = "Agent Response"

            # Filter or Highlight SDET
            # On cherche à voir si c'est le SDET qui consomme
            # Mais le log actuel ne contient pas le nom de l'agent explicite dans le header [AGENT]
            # C'est l'outil qui est loggué.
            # Cependant, si on voit "RunPlaywright" ou "VideoResource", c'est un indice.
            
            tokens = len(encoding.encode(req))
            total_tokens += tokens
            
            preview = req.replace('\n', ' ')[:50] + "..."
            
            # Afficher tout pour l'instant
            print(f"{name:<40} | {tokens:<10} | {preview:<30}")

        print("-" * 90)
        print(f"{'TOTAL SESSIONS':<40} | {total_tokens:<10}")

    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    analyze_requests("output/gemini_requests.log")
