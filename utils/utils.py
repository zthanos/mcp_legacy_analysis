import re
import json
from pathlib import Path

import os

def languages_from_json(filepath: str) -> dict:
    import json
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
    
WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

def extract_json_from_text(text):
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not matches:
        raise ValueError("No valid JSON found in LLM response")
    return json.loads(matches[0])    

def safe_read_file(file_path):
    for encoding in ['utf-8', 'cp1252', 'iso-8859-1', 'cp037']:
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                return f.read(), encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None, None


def get_file_content_full_path(full_path: str) -> str:
    with open(full_path, "r") as f:
        return f.read()

def get_file_content(repository_name: str, filename: str) -> str:
    """
    Helper function to retrieve file content from the repository.
    This is used internally by the retrieve_file_content tool.
    """
    try:
        repo_path = WORKSPACE / repository_name
        
        # Handle both absolute and relative paths
        if os.path.isabs(filename):
            file_path = Path(filename)
        else:
            # Search for the file in the repository
            file_path = None
            for root, dirs, files in os.walk(repo_path):
                if filename in files:
                    file_path = Path(root) / filename
                    break
            
            if file_path is None:
                return f"ERROR: File '{filename}' not found in repository '{repository_name}'"
        
        if not file_path.exists():
            return f"ERROR: File not found: {file_path}"
        
        # Try to read the file with different encodings
        content = ""
        encoding_used = ""
        
        for encoding in ['utf-8', 'cp1252', 'iso-8859-1', 'cp037']:  # cp037 for EBCDIC
            try:
                with open(file_path, "r", encoding=encoding, errors="replace") as f:
                    content = f.read()
                encoding_used = encoding
                break
            except (UnicodeDecodeError, UnicodeError):
                continue
        
        if not content and not encoding_used:
            # Try binary mode as last resort
            with open(file_path, "rb") as f:
                raw_content = f.read()
                content = raw_content.decode('utf-8', errors='replace')
                encoding_used = "binary (utf-8 fallback)"
        
        return content
        
    except Exception as e:
        return f"ERROR: Unable to retrieve file content: {str(e)}"    
