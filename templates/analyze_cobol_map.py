from pathlib import Path
import re

def extract_useful_bms_lines(content: str) -> str:
    """
    Κρατά μόνο:
    - MAP όνομα από DFHMDI
    - Όλες τις labeled DFHMDF γραμμές
    """
    lines = content.splitlines()
    useful_lines = []
    inside_map = False

    for line in lines:
        stripped = line.strip()

        # Βρίσκει το MAP όνομα (DFHMDI δήλωση)
        if re.match(r'^[A-Z0-9]+ +DFHMDI', stripped):
            useful_lines.append(stripped)
            inside_map = True

        # Βρίσκει labeled DFHMDF πεδία
        elif inside_map and re.match(r'^[A-Z0-9\-]+ +DFHMDF', stripped):
            useful_lines.append(stripped)

    return "\n".join(useful_lines)


def prepare_bms_analysis_prompt(clean_content: str) -> tuple[str, str]:
    system_prompt = "You are an expert in COBOL, HLASM, and CICS BMS MAP screen parsing. Output only valid JSON, no explanations."

    llm_message = f"""
I will provide a filtered BMS copybook definition written in HLASM syntax.

Your task:
- Locate all labeled DFHMDF fields
- Output a JSON array with:
    - `name`: Field name as defined before DFHMDF
    - `type`: 'X' for alphanumeric, '9' for numeric
    - `size`: Length from LENGTH attribute
    - `sudoType`: Pseudocode description (e.g., String(10), Character(1), Numeric(5))
    - `struct_name`: `<map_name>I.<field_name>I` or `<map_name>O.<field_name>O`

Output only valid JSON in a triple backtick block like:

```json
[
  {{"name": "OPTION", "type": "X", "size": 1, "sudoType": "Character(1)", "struct_name": "DOGEDT1I.OPTIONI"}}
]
```

---BMS START---
{extract_useful_bms_lines(clean_content)}
---BMS END---

Return only the JSON array as described.
"""
    return system_prompt, llm_message



# def analyze_map_template(content: str) -> tuple[str, str]:
#     system_prompt = "You are an expert in legacy IBM mainframe development, HLASM, and CICS BMS MAP screen generation."

#     llm_message = f"""
# I will provide you with a BMS Map copybook definition written in HLASM (High Level Assembler) syntax.

# Your ONLY task is to:
# - ** IGNORE ** all the lines that are not related to the BMS Map copybook. visual data, etc.
# - Locate all labeled DFHMDF fields from the BMS copybook
# - For each labeled field, output a JSON object with:
#     - `name`: Field name as defined before DFHMDF
#     - `type`: 'X' for alphanumeric, '9' for numeric
#     - `size`: Length in characters from LENGTH attribute
#     - `sudoType`: Human-readable pseudocode type
#     - `struct_name`: Full COBOL reference in the format `<map_name>I.<field_name>I` or `<map_name>O.<field_name>O`

# Output ONLY a valid JSON array enclosed in triple backticks, nothing else.

# The BMS source may contain unusual symbols (`$`, `"`, `^`) — IGNORE them unless they affect the field definitions.

# Quick HLASM syntax reminders:
# - Lines use continuation with `X` at the end.
# - Fields are defined with `DFHMDF`.
# - Labeled fields have a name before `DFHMDF` (e.g., `OPTION DFHMDF ...`).
# - Relevant attributes include `POS`, `LENGTH`, `COLOR`, and `ATTRB`.
# - Only labeled fields correspond to COBOL variables.

# For each labeled field, output a JSON object with:
# - `name`: Original BMS field name (e.g., OPTION, KEY).
# - `type`: Simplified COBOL Picture type:
#     - 'X' for alphanumeric
#     - '9' for numeric
# - `size`: Length in characters, based on the LENGTH attribute.
# - `sudoType`: Human-readable pseudocode type for understanding:
#     - If type is 'X' and size = 1 → `Character(size)`
#     - If type is 'X' and size > 1 → `String(size)`
#     - If type is '9' → `Numeric(size)`
#     - If type starts with 'S9' → `Signed Numeric(size)`
# - `struct_name`: The full COBOL reference, based on:
#     - `<map_name>I.<field_name>I` for input fields (if ATTRB contains UNPROT)
#     - `<map_name>O.<field_name>O` for output fields (if ATTRB contains PROT but not UNPROT)

# The MAP name is the label used in the `DFHMDI` statement.

# **Output Format:**
# Return only valid JSON, enclosed within triple backticks, like:

# ```json
# [
#   {{"name": "OPTION", "type": "X", "size": 1, "sudoType": "Character(1)", "struct_name": "DOGEDT1I.OPTIONI"}},
#   {{"name": "KEY", "type": "X", "size": 10, "sudoType": "String(10)", "struct_name": "DOGEDT1I.KEYI"}}
# ]
# Do NOT output explanations, code examples unrelated to the JSON, or formatting instructions.

# ---BMS COPYBOOK INPUT START---
# {content}
# ---BMS COPYBOOK INPUT END---

# """
#     return system_prompt, llm_message    