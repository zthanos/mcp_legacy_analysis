
    
def clist_flow_extraction(source_code: str) -> str:

  system_prompt = "You are an expert mainframe programmer and CLIST (Command List) analyst with deep knowledge of TSO/ISPF scripting."
  llm_messages = f"""
Your task is to analyze the provided CLIST code and extract its execution flow, starting from its primary entry points.

CLIST is a TSO command procedure language that supports:
- PROC statements (procedure definitions)
- Control statements (IF/THEN/ELSE, DO/END, SELECT/WHEN/OTHERWISE)
- TSO commands and utilities
- Variable definitions and assignments (&VAR)
- Built-in functions (&SYSDSN, &STR, &SUBSTR, etc.)
- SYSCALL and INVOKE statements
- GOTO and label statements
- Error handling (ERROR, ATTENTION statements)

Represent the flow as a directed graph in JSON format, where:
- Each node is a CLIST procedure, control block, label, or command section.
- Each edge represents a control flow transfer (e.g., procedure call, conditional execution, loop, goto).
- For each node, include its type (e.g., "proc", "main_block", "if_block", "do_loop", "select_block", "label", "command_sequence").
- For each edge, specify the type of transfer (e.g., "CALL", "CONDITIONAL", "LOOP", "GOTO", "SELECT_WHEN", "ERROR_HANDLER").
- Identify entry points (PROC statements or main execution flow).
- Track variable usage and parameter passing.
- Include TSO command invocations and utility calls.
- Handle error flows and attention exits.

CLIST CODE:
{source_code}

Please return the JSON output only, ensuring it's valid and complete.
The JSON should contain:
{{
  "main_entry_points": ["MAIN", "PROC_NAME"],
  "procedures": ["PROC1", "PROC2"],
  "variables": ["&VAR1", "&VAR2"],
  "tso_commands": ["ALLOC", "FREE", "LISTDS"],
  "labels": ["LABEL1", "ERROR_EXIT"],
  "flow_graph": [
    {{
      "node": "MAIN",
      "type": "main_block",
      "is_entry_point": true,
      "line_number": 1,
      "variables_defined": ["&INPUT", "&OUTPUT"],
      "edges_to": [
        {{"target": "VALIDATE_PARMS", "transfer_type": "CALL", "line_number": 5}},
        {{"target": "IF_BLOCK_1", "transfer_type": "CONDITIONAL", "condition": "&INPUT NE", "line_number": 10}}
      ]
    }},
    {{
      "node": "VALIDATE_PARMS",
      "type": "proc",
      "is_entry_point": false,
      "parameters": ["&PARM1", "&PARM2"],
      "line_number": 50,
      "edges_to": [
        {{"target": "ERROR_EXIT", "transfer_type": "GOTO", "condition": "validation_failed", "line_number": 55}},
        {{"target": "RETURN", "transfer_type": "RETURN", "line_number": 60}}
      ]
    }},
    {{
      "node": "IF_BLOCK_1",
      "type": "if_block",
      "is_entry_point": false,
      "condition": "&INPUT NE",
      "line_number": 10,
      "edges_to": [
        {{"target": "PROCESS_INPUT", "transfer_type": "THEN", "line_number": 12}},
        {{"target": "ERROR_EXIT", "transfer_type": "ELSE", "line_number": 15}}
      ]
    }},
    {{
      "node": "DO_LOOP_1",
      "type": "do_loop",
      "is_entry_point": false,
      "loop_variable": "&I",
      "loop_condition": "&I = 1 TO &COUNT",
      "line_number": 20,
      "edges_to": [
        {{"target": "PROCESS_ITEM", "transfer_type": "LOOP_BODY", "line_number": 22}},
        {{"target": "CLEANUP", "transfer_type": "LOOP_EXIT", "line_number": 30}}
      ]
    }},
    {{
      "node": "ERROR_EXIT",
      "type": "label",
      "is_entry_point": false,
      "line_number": 100,
      "edges_to": [
        {{"target": "CLEANUP", "transfer_type": "SEQUENCE", "line_number": 102}},
        {{"target": "EXIT", "transfer_type": "EXIT", "line_number": 110}}
      ]
    }}
  ]
}}
"""
  return system_prompt, llm_messages