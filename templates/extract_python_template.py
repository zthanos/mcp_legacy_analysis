def python_flow_extraction(source_code: str, filename: str, program_id: str="program_id") -> tuple[str, str]:

    system_prompt = (
        "You are an expert in Python programming, static code analysis, and legacy system mapping.\n"
        "Your task is to extract the execution flow of the provided Python source code and produce a valid JSON representation.\n"
        "This analysis is for system-wide integration mapping and impact assessment, especially detecting external dependencies.\n"
    )

    llm_messages = f"""
Analyze the following Python source code strictly based on the provided content (static analysis only, no assumptions).

Your output must be a valid JSON matching this structure:

{{
  "program_id": "{program_id}",
  "filename": "{filename}",
  "language": "Python",
  "main_entry_points": ["list of detected main entry points (e.g., '__main__', 'main')"],
  "flow_graph": [
    {{
      "node": "function, method, class, or block name",
      "type": "function | method | class | main_block | conditional | loop | exception_handler",
      "is_entry_point": true | false,
      "edges_to": [
        {{
          "target": "next node name",
          "transfer_type": "CALL | METHOD_CALL | INSTANTIATION | CONDITIONAL | LOOP | EXCEPTION_HANDLER",
          "integration_type": "internal | external-db | external-service | external-program | external-other",
          "external_system": "system name (e.g., PostgreSQL, REST API) or null"
        }}
      ]
    }}
  ],
  "path_to_critical": [
    {{
      "critical_node": "node name leading to external interaction",
      "external_system": "system name (e.g., PostgreSQL, REST API)",
      "path": [
        {{
          "node": "intermediate node name",
          "condition": "execution condition to reach next node or null"
        }}
      ]
    }}
  ]
}}

Guidelines:
- Identify all entry points (e.g., "__main__", top-level functions, async entrypoints).
- Map each function, method, class, or control structure as a node.
- Detect external interactions, including:
    - Database connections (e.g., PostgreSQL, MySQL)
    - API calls (e.g., requests, httpx, external libraries)
    - System calls or subprocess executions
- Set `"integration_type"` accordingly:
    - `"internal"` for code-internal transfers
    - `"external-db"` for database access
    - `"external-service"` for API/web service calls
    - `"external-program"` for subprocess or external executable calls
    - `"external-other"` for other external dependencies
- Leave `"external_system"` as `null` if the system name is not identifiable from the code.
- In `path_to_critical`, document all execution paths leading to external interactions, with conditions where applicable.

PYTHON CODE:
```python
{source_code}
```


Your response must be valid JSON, no extra text or explanations.
"""

    return system_prompt, llm_messages
