
from templates.extract_cobol_template import cobol_flow_extraction
from templates.extract_clist_template import clist_flow_extraction
from templates.extract_python_template import python_flow_extraction

def get_flow_extraction_prompt(filename: str, classification: str, source_code: str) -> str:
    classification = classification.lower()
    if classification == "cobol":
        return cobol_flow_extraction(filename=filename, source_code=source_code)
    elif classification == "clist":
        return clist_flow_extraction(filename=filename, source_code=source_code)    
    elif classification == "python":
        return python_flow_extraction(filename=filename, source_code=source_code)
    else:
        raise ValueError(f"Unknown classification: {classification}")