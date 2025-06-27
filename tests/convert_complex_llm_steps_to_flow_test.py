from tests.process_flow_response import complex_mock
from helpers.llm_to_flow_graph import convert_llm_steps_to_flow
import json



converted_complex = convert_llm_steps_to_flow("workspace\\DOGECICS\\COBOL\\DOGEMAIN", complex_mock)
import json
print(json.dumps(converted_complex, indent=2))