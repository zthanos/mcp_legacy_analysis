from pathlib import Path
    
def classify_file_template(filename, content: str, repository: str) -> tuple[str, str]:
    system_prompt = "You are an expert in programming languages and file formats, including legacy systems such as COBOL, CLIST, JCL, BMS maps, and other mainframe technologies."
    llm_message = f"""
### You must return ONLY a JSON object with the following format:

{{
  "filename": "example.cbl",
  "repository": "SAMPLE-REPO",
  "classification": "Programming Language source file",
  "language": "COBOL",
  "description": "Main COBOL program for processing transactions"
}}

### Rules:
- classification: one of ["Programming Language source file", "JCL Script", "BMS Map", "Copybook", "Text File", "Unknown"]
- language: one of ["COBOL", "CLIST", "JCL", "Java", "Python", "None", "Unknown"]
- Return **JSON only**. Do NOT add explanations.
- Use the content preview below to decide, but do not include it in output.

### File Metadata:
- filename: {filename}
- repository: {repository}
- file extension: {Path(filename).suffix}

### File Content (DO NOT OUTPUT THIS):
---START FILE PREVIEW---
{content[:1500]}
---END FILE PREVIEW---

### OUTPUT ONLY THE JSON OBJECT BELOW:
---END---

Now return the JSON object:
"""
    return system_prompt, llm_message


    