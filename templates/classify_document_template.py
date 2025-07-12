from pathlib import Path

def classify_document_template(filename, content: str, repository: str) -> tuple[str, str]:
    system_prompt = """
You are an expert in programming languages and file formats, including legacy mainframe technologies 
(COBOL, CLIST, JCL, BMS maps, Copybooks) and modern languages (C#, Java, Python, etc.).

### GOAL:
Classify the file precisely as source code, script, or other, using syntax, keywords, and structure.
Do NOT rely only on filename or extension.

### FORMAT TO RETURN:
{
  "filename": "<filename>",
  "repository": "<repository>",
  "classification": "<one of: Programming Language source file, JCL Script, BMS Map, Copybook, CLIST Script, Text File, Unknown>",
  "language": "<one of: COBOL, CLIST, JCL, C#, Java, Python, None, Unknown>",
  "description": "<short explanation, e.g., 'COBOL batch program', 'CLIST script for TSO automation', 'C# class library'>"
}

### KEY IDENTIFICATION HINTS:

- COBOL:
  - 'IDENTIFICATION DIVISION', 'PROCEDURE DIVISION', 'DATA DIVISION'
  - Keywords: 'PERFORM', 'MOVE', 'IF', 'CALL'
  - Fixed column format, often with line numbers, '*' in column 7

- CLIST:
  - Starts with 'PROC 0' or 'PROC 1'
  - Uses TSO commands: 'ALLOC', 'FREE', 'CONTROL'
  - Variables: '&NAME'
  - Comments: '/* comment */'

- JCL:
  - Lines start with '//'
  - Contains EXEC, DD, JOB statements

- C#:
  - 'using System;', 'namespace', 'class', 'public', 'void'
  - Uses { } for blocks

- Java:
  - 'package', 'import', 'public class', 'extends', 'implements'

- Python:
  - 'def', 'import', indentation-based, no semicolons

- BMS Map:
  - DFHMDI, DFHMDF, POS, ATTRB

- Copybook:
  - COBOL declarations only, no PROCEDURE DIVISION, many 01, 05, 10 levels

- Text File:
  - No recognizable syntax

### RULES:
- If unsure, use 'Unknown'.
- Decide based on file content, not just extension.
- OUTPUT ONLY THE JSON OBJECT. DO NOT include explanations.

"""

    llm_message = f"""
### FILE METADATA:
- filename: {filename}
- repository: {repository}
- file extension: {Path(filename).suffix}

### FILE PREVIEW (DO NOT OUTPUT THIS):
---START PREVIEW---
{content[:1500]}
---END PREVIEW---

Now return the JSON object:
"""

    return system_prompt, llm_message
