import os
import requests
import subprocess
import json
import sys
import time

def query_mcp_http(prompt: str) -> str:
    """
    Στέλνει το prompt στον MCP server μέσω HTTP και επιστρέφει την απάντηση.
    Ο MCP server πρέπει να τρέχει με transport 'http' (π.χ. --transport http --port 8000).
    """
    mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/request")
    
    try:
        payload = {"prompt": prompt}
        headers = {"Content-Type": "application/json"}
        
        resp = requests.post(mcp_url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        
        data = resp.json()
        return data.get("response", data.get("result", "Δεν βρέθηκε απάντηση"))
        
    except requests.exceptions.ConnectionError:
        return "Σφάλμα: Ο MCP server δεν είναι προσβάσιμος. Βεβαιωθείτε ότι τρέχει στο http://localhost:8000"
    except requests.exceptions.Timeout:
        return "Σφάλμα: Timeout - Ο MCP server δεν απάντησε εγκαίρως"
    except requests.exceptions.RequestException as e:
        return f"Σφάλμα HTTP επικοινωνίας με MCP server: {e}"
    except json.JSONDecodeError:
        return "Σφάλμα: Μη έγκυρη JSON απάντηση από τον MCP server"


def query_mcp_stdio(prompt: str) -> str:
    """
    Στέλνει το prompt στον MCP server μέσω STDIO.
    Εκκινήστε τον server με transport 'stdio'.
    
    Χρήση:
      export MCP_SERVER_CMD="python your_server.py"
      export MCP_USE_STDIO=true
    """
    cmd = os.getenv("MCP_SERVER_CMD", "python main.py")
    
    try:
        # Δημιουργία του process
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            bufsize=0  # Unbuffered για άμεση επικοινωνία
        )
        
        # Προετοιμασία του αιτήματος
        request_data = {"prompt": prompt}
        request_json = json.dumps(request_data) + "\n"
        
        # Αποστολή και λήψη απάντησης
        try:
            out, err = proc.communicate(input=request_json, timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            return "Σφάλμα: Timeout - Ο MCP server δεν απάντησε εγκαίρως"
        
        # Έλεγχος για σφάλματα
        if proc.returncode != 0:
            return f"MCP STDIO error (return code {proc.returncode}): {err.strip()}"
        
        if err.strip():
            print(f"MCP STDIO warning: {err.strip()}", file=sys.stderr)
        
        # Επεξεργασία της εξόδου
        if not out.strip():
            return "Σφάλμα: Κενή απάντηση από τον MCP server"
        
        # Αναζήτηση για έγκυρο JSON στην έξοδο
        json_response = None
        for line in out.splitlines():
            line = line.strip()
            if line and (line.startswith('{') or line.startswith('[')):
                try:
                    json_response = json.loads(line)
                    break
                except json.JSONDecodeError:
                    continue
        
        if json_response is None:
            # Αν δεν βρέθηκε JSON, επιστροφή του raw output
            return out.strip()
        
        # Εξαγωγή της απάντησης από το JSON
        if isinstance(json_response, dict):
            return json_response.get("response", 
                   json_response.get("result", 
                   json_response.get("output", str(json_response))))
        else:
            return str(json_response)
            
    except FileNotFoundError:
        return f"Σφάλμα: Δεν βρέθηκε η εντολή '{cmd}'. Ελέγξτε το MCP_SERVER_CMD."
    except Exception as e:
        return f"Σφάλμα STDIO επικοινωνίας με MCP server: {e}"


def query_ollama(prompt: str) -> str:
    """
    Στέλνει το prompt στον Ollama HTTP API και επιστρέφει την απάντηση.
    Βεβαιωθείτε ότι έχετε τρέξει `ollama serve`.
    """
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/chat/completions")
    model = os.getenv("OLLAMA_MODEL", "deepseek-coder")
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    try:
        resp = requests.post(ollama_url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        
        data = resp.json()
        
        # Διαφορετικά formats ανάλογα με την έκδοση του Ollama API
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["message"]["content"]
        elif "response" in data:
            return data["response"]
        else:
            return f"Μη αναμενόμενη δομή απάντησης: {data}"
            
    except requests.exceptions.ConnectionError:
        return "Σφάλμα: Ο Ollama server δεν είναι προσβάσιμος. Εκτελέστε 'ollama serve'"
    except requests.exceptions.Timeout:
        return "Σφάλμα: Timeout - Ο Ollama server δεν απάντησε εγκαίρως"
    except requests.exceptions.RequestException as e:
        return f"Σφάλμα στην επικοινωνία με Ollama: {e}"
    except json.JSONDecodeError:
        return "Σφάλμα: Μη έγκυρη JSON απάντηση από τον Ollama server"


def check_servers():
    """Ελέγχει την κατάσταση των servers"""
    print("Έλεγχος κατάστασης servers...")
    
    # Έλεγχος MCP server
    use_stdio = os.getenv("MCP_USE_STDIO", "false").lower() == "true"
    if use_stdio:
        print("✓ MCP: Configured για STDIO transport")
        mcp_cmd = os.getenv("MCP_SERVER_CMD", "python your_server.py")
        print(f"  Command: {mcp_cmd}")
    else:
        mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000/request")
        try:
            resp = requests.get(mcp_url.replace('/request', '/health'), timeout=5)
            print(f"✓ MCP: Προσβάσιμος στο {mcp_url}")
        except:
            print(f"✗ MCP: Μη προσβάσιμος στο {mcp_url}")
    
    # Έλεγχος Ollama server
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/chat/completions")
    try:
        test_url = ollama_url.replace('/v1/chat/completions', '/api/tags')
        resp = requests.get(test_url, timeout=5)
        print(f"✓ Ollama: Προσβάσιμος στο {ollama_url}")
    except:
        print(f"✗ Ollama: Μη προσβάσιμος στο {ollama_url}")
    
    print()


def main():
    print("Πρόγραμμα ερωτήσεων σε MCP server & Ollama")
    print("=" * 50)
    
    # Έλεγχος servers
    check_servers()
    
    print("Πληκτρολογήστε 'exit' για έξοδο, 'status' για έλεγχο servers.")
    print("Περιβαλλοντικές μεταβλητές:")
    print(f"  MCP_USE_STDIO: {os.getenv('MCP_USE_STDIO', 'false')}")
    print(f"  MCP_SERVER_URL: {os.getenv('MCP_SERVER_URL', 'http://localhost:8000/request')}")
    print(f"  MCP_SERVER_CMD: {os.getenv('MCP_SERVER_CMD', 'python your_server.py')}")
    print(f"  OLLAMA_MODEL: {os.getenv('OLLAMA_MODEL', 'deepseek-coder')}")
    print()
    
    use_stdio = os.getenv("MCP_USE_STDIO", "false").lower() == "true"
    
    while True:
        try:
            prompt = input("> ").strip()
            
            if prompt.lower() in {"exit", "quit", "q"}:
                print("Αντίο!")
                break
            
            if prompt.lower() == "status":
                check_servers()
                continue
                
            if not prompt:
                continue
            
            print("\n" + "=" * 50)
            
            # 1) Ερώτηση στον MCP server
            print("🔍 Ερώτηση στον MCP server...")
            start_time = time.time()
            
            if use_stdio:
                mcp_resp = query_mcp_stdio(prompt)
            else:
                mcp_resp = query_mcp_http(prompt)
            
            mcp_time = time.time() - start_time
            print(f"📝 MCP απάντηση ({mcp_time:.2f}s):")
            print(f"{mcp_resp}\n")
            
            # 2) Ερώτηση κατευθείαν στον Ollama
            print("🤖 Ερώτηση στον Ollama...")
            start_time = time.time()
            
            ollama_resp = query_ollama(prompt)
            
            ollama_time = time.time() - start_time
            print(f"🦙 Ollama απάντηση ({ollama_time:.2f}s):")
            print(f"{ollama_resp}\n")
            
        except KeyboardInterrupt:
            print("\n\nΔιακοπή από τον χρήστη. Αντίο!")
            break
        except Exception as e:
            print(f"Απρόσμενο σφάλμα: {e}")
            continue


if __name__ == "__main__":
    main()