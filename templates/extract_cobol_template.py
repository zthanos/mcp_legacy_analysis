
    
def cobol_flow_extraction(source_code: str) -> str:
    return {
        "system_prompt": "You are an expert COBOL programmer and a seasoned static analysis tool.", 
        "llm_messages": f"""
Your task is to analyze the provided COBOL code and extract its execution flow, starting from its primary entry point (typically the first executable statement after PROCEDURE DIVISION, or an explicit ENTRY point).

Represent the flow as a directed graph in JSON format, where:
- Each node is a COBOL paragraph, section, or program/subprogram name.
- Each edge represents a control flow transfer (e.g., PERFORM, CALL, GO TO, implicit fall-through).
- For each node, include its type (e.g., "paragraph", "section", "program").
- For each edge, specify the type of transfer (e.g., "PERFORM", "CALL", "GO TO", "FALLTHROUGH").
- If a method is an entry point, include that information for the corresponding node.
- Identify the main entry point(s) of the program.

COBOL CODE:
{source_code}

Please return the JSON output only, ensuring it's valid and complete.
The JSON should contain:
{{
"main_entry_points": ["MAIN-PROG-ENTRY"],
"flow_graph": [
    {{
    "node": "MAIN-PROG-ENTRY",
    "type": "program",
    "is_entry_point": true,
    "edges_to": [
        {{"target": "INITIALIZE-ROUTINE", "transfer_type": "FALLTHROUGH"}},
        {{"target": "PROCESS-RECORDS", "transfer_type": "PERFORM"}}
    ]
    }},
    {{
    "node": "INITIALIZE-ROUTINE",
    "type": "paragraph",
    "is_entry_point": false,
    "edges_to": [
        {{"target": "READ-INPUT-FILE", "transfer_type": "CALL"}},
        {{"target": "SETUP-VARIABLES", "transfer_type": "PERFORM"}}
    ]
    }}
    // ... more nodes and edges
]
}}
"""
}