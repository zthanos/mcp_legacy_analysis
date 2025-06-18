from pathlib import Path
import os
from sampling import sample_helper
from templates.extract_cobol_template import cobol_flow_extraction

WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

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

async def classify_file(content: str, filename: str, ctx) -> str:
    try:    
        system_prompt, messages_for_llm = cobol_flow_extraction(filename=filename, content=content)
        response = await sample_helper(ctx=ctx, messages_for_llm=messages_for_llm, system_prompt=system_prompt, temperature=0.7)

        if not response:
            await ctx.error("Empty response from LLM")
            return "Error: Empty response from LLM"

            
        return response.text.strip().splitlines()[0]


    except Exception as e:
        return f"Error: Unable to classify file due to processing error: {str(e)}"    