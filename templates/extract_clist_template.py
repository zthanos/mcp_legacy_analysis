def clist_flow_extraction(filename: str, source_code: str) -> tuple[str, str]:
    system_prompt = (
        "You are an expert in analyzing TSO/ISPF CLIST scripts for execution flow extraction.\n"
        "Your task is to extract the control flow of the provided CLIST script and represent it as a directed graph.\n"
        "Focus on control structures (IF, DO, SELECT), label jumps (GOTO), procedure calls, and system command execution.\n"
        "Ensure output follows exactly the JSON structure below, matching the COBOL model for system-wide consistency."
    )

    llm_message = f"""
Analyze the following CLIST script and return a valid JSON matching this structure:

{{
  "filename": "{filename}",
  "language": "CLIST",
  "main_entry_points": ["MAIN"],
  "flow_graph": [
    {{
      "node": "MAIN",
      "type": "program",
      "is_entry_point": true,
      "edges_to": [
        {{
          "target": "VALIDATE-PARAMS", 
          "transfer_type": "CALL", 
          "integration_type": "internal",
          "condition": "&PARAM_VALID", 
          "line_number": 45
        }},
        {{
          "target": "FILE-ALLOCATION", 
          "transfer_type": "COMMAND", 
          "command": "ALLOC", 
          "integration_type": "file",
          "line_number": 32
        }}
      ]
    }},
    {{
      "node": "HANDLE-ERROR",
      "type": "label",
      "is_entry_point": false,
      "line_number": 120,
      "edges_to": [
        {{
          "target": "EXIT", 
          "transfer_type": "RETURN", 
          "integration_type": "internal",
          "line_number": 125
        }}
      ]
    }}
  ]
}}

**Analysis Rules:**
1. Identify ALL control flow elements including:
   - PROC statements (main entry points)
   - IF/THEN/ELSE blocks (with conditions)
   - DO/END groups
   - GOTO statements and their targets
   - CALL invocations
   - System commands (ALLOC/FREE/CONTROL)
   - Error handling sections

2. For each node:
   - Include exact line numbers
   - Mark conditions for conditional branches
   - Specify command types for system interactions
   - Preserve the original nesting structure

3. Special handling for:
   - File operations (mark as integration_type='file')
   - TSO command sequences
   - Nested control structures
   - Error handling flows

CLIST CODE:
{source_code}

Only return the valid JSON in the structure shown above.
"""

    return system_prompt, llm_message