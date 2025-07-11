from utils.utils import languages_from_json
import uuid

def get_code_analysis_prompt(document, repository_name: str) -> str:
    return f"""
# MCP Server Language-Aware Code Analysis Prompt

## System Instructions

You are a language-agnostic static code analyzer operating within the MCP Server.

### Analysis Workflow

1. **Identify Programming Language**
   - Use the tool `get_document_info` with repository: `{repository_name}`, filename: `{document}`
   - This returns metadata including detected language (e.g., Python, COBOL, CLIST, C)

2. **Retrieve Source Code**
   - Use `retrieve_file_content` with `{repository_name}` and `{document}`
   - Assign the result to `source_code`

3. **Language-Specific Analysis**
   - Based on the detected language, invoke `get_language_specific_prompt(language, source_code, filename, repository_name)`
   - Use the returned prompt template for that language to perform in-depth static analysis

4. **Produce JSON Output**
   - Output strictly valid JSON as per the language-agnostic schema:
   
```json
{{
  "program_id": "unique program/module identifier",
  "filename": "{document}",
  "language": "detected language",
  "main_entry_points": ["entry points list"],
  "flow_graph": [...],
  "path_to_critical": [...]
}}
"""    

def prepare_document_analysis_prompt(source_code: str, filename: str, repository_name: str, program_id: str, language: str) -> tuple[str, str]:
    supported = languages_from_json("languages_config.json")
    if language not in supported:
        raise ValueError(f"Unsupported language: {language}")
    if language not in supported:
        raise ValueError(f"Unsupported language: {language}")

    system_prompt = prepare_common_system_prompt(language)
    entry_points_hint = supported[language]["entry_points_hint"]
    analysis_rules = supported[language]['analysis_rules']
    llm_message = generate_common_json_template(program_id, filename, repository_name, language, entry_points_hint, source_code, analysis_rules)

    return system_prompt, llm_message


def prepare_common_system_prompt(language: str) -> str:
    return f"You are a {language} static code analysis expert for legacy systems. Extract execution flow, external interactions, inheritance, and critical paths."

def processed_data_to_json(llm_response: str) -> str:
  return """
Based on the following analysis, generate structured JSON with the following schema:

{
  "purpose": string,
  "impact_analysis": {
    "internal_operations": [string],
    "external_interactions": [string]
  },
  "integrations": {
    "systems": [
      {
        "type": string,
        "system": string,
        "interactions": [string]
      }
    ]
  },
  "critical_paths": [string]
}

Use only the information from the analysis provided. Do not invent new data.

Analysis:
{llm_response}
  """


def generate_common_json_template(program_id: str, filename: str, repository_name: str, language: str, entry_points_hint: str, source_code: str, analysis_rules: str) -> str:
    unique_id = uuid.uuid4()
    language = language if language else ""
    return f"""

Review Session {unique_id} – Expert Legacy Integration Analysis

You are a senior {language} Engineer.

Your task is to perform a **code review** on the following script.

Please identify and explain:

- The overall **purpose** of the script
- Key **internal operations**, especially main flows or steps
- Any **external system integrations** (e.g. RPC, socket, JCL, file I/O)
- Which **data** is being read, generated, or transmitted
- Any dependencies or technologies involved (e.g., Dogecoin wallet, TK4-, VSAM)
- Any architectural or integration patterns used

Be precise and use only the information from the code. Do **not assume functionality** that is not evident in the source.

Present the review in clearly separated sections using titles like:
`Purpose`, `Internal Operations`, `Integrations`, `Dependencies`, `Execution Flow`, `Notes`.

Do not reuse cached knowledge. Treat this as a brand-new review.


{language} CODE:
```{language}
{source_code}
```

"""