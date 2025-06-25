from pathlib import Path
import os
from sampling import sample_helper
from templates.classify_file_template import classify_file_template
from templates.analyze_cobol_map import prepare_bms_analysis_prompt

WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

def get_file_content_full_path(full_path: str) -> str:
    with open(full_path, "r") as f:
        return f.read()

def get_file_content(repository_name: str, filename: str) -> str:
    """
    Helper function to retrieve file content from the repository.
    This is used internally by the retrieve_file_content tool.
    """
    try:
        repo_alias = repository_name.replace("resource://", "")
        repo_path = WORKSPACE / repo_alias
        
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

async def classify_file(content: str, filename: str, repository: str, ctx) -> str:
    try:    
        system_prompt, messages_for_llm = classify_file_template(filename=filename, content=content, repository=repository)
        response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0.7)

        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"

            
        return response.strip()


    except Exception as e:
        return f"Error: Unable to classify file due to processing error: {str(e)}"    

async def analyze_map(full_path: str, ctx) -> str:
    try:    
        print(f"full_path: {full_path}")
        print("--------------------------------")
        content = get_file_content_full_path(full_path)    
        system_prompt, messages_for_llm = prepare_bms_analysis_prompt(content)
        print(f"content: {messages_for_llm}")
        print("--------------------------------")        
        response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0)

        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"

            
        return response.strip()


    except Exception as e:
        return f"Error: Unable to classify file due to processing error: {str(e)}"    
