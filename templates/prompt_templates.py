
from templates.extract_cobol_template import cobol_flow_extraction

def get_flow_extraction_prompt(classification: str, source_code: str) -> str:
    if classification == "cobol":
        return cobol_flow_extraction(source_code)
    else:
        raise ValueError(f"Unknown classification: {classification}")