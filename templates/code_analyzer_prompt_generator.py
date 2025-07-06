# Unified Language-Specific Prompts for MCP Static Analysis



def generate_common_json_template(program_id: str, filename: str, repository_name: str, language: str, entry_points_hint: str, source_code: str) -> str:
    return f"""
Produce valid JSON in this format:
{{
  "program_id": "{program_id}",
  "filename": "{filename}",
  "repository_name": "{repository_name}",
  "language": "{language}",
  "main_entry_points": [{entry_points_hint}],
  "flow_graph": [
    {{
      "node": "function, method, class, interface, controller, service, repository, block",
      "type": "function | method | class | interface | controller | service | repository | block | conditional | loop | exception_handler | program | paragraph | section | label",
      "is_entry_point": true | false,
      "inheritance": {{"extends": "parent class or null", "implements": ["interface1", "interface2"]}},
      "edges_to": [
        {{
          "target": "next node",
          "transfer_type": "CALL | METHOD_CALL | INSTANTIATION | CONDITIONAL | LOOP | EXCEPTION_HANDLER | PERFORM | FALLTHROUGH | GOTO | COMMAND",
          "integration_type": "internal | external-db | external-service | external-program | external-other | file",
          "external_system": "system name or null",
          "condition": "condition or null",
          "line_number": line number or null
        }}
      ]
    }}
  ],
  "path_to_critical": [
    {{
      "critical_node": "external interaction node",
      "external_system": "system name",
      "path": [{{"node": "intermediate", "condition": "condition or null"}}]
    }}
  ]
}}

{language} CODE:
{source_code}

Only return valid JSON.
"""
def languages_from_json(filepath: str) -> dict:
    import json
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
    


def generate_common_system_prompt(language: str) -> str:
    return f"You are a {language} static code analysis expert for legacy systems. Extract execution flow, external interactions, inheritance, and critical paths."

def flow_extraction(source_code: str, filename: str, repository_name: str, program_id: str, language: str) -> tuple[str, str]:
    supported = languages_from_json("languages_config.json")
    if language not in supported:
        raise ValueError(f"Unsupported language: {language}")
    if language not in supported:
        raise ValueError(f"Unsupported language: {language}")

    system_prompt = generate_common_system_prompt(language)
    print(f"system_prompt: {system_prompt}")
    entry_points_hint = supported[language]["entry_points_hint"]
    llm_message = generate_common_json_template(program_id, filename, repository_name, language, entry_points_hint, source_code)

    return system_prompt, llm_message
