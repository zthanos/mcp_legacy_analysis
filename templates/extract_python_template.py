
    
def cobol_flow_extraction(source_code: str) -> str:
    return {
        "system_prompt": "You are an expert Python programmer and a seasoned static analysis tool.", 
        "llm_messages": f"""
Your task is to analyze the provided Python code and extract its execution flow, starting from its primary entry points (such as if __name__ == "__main__", function definitions, class methods, etc.).

Represent the flow as a directed graph in JSON format, where:
- Each node is a Python function, method, class, or code block name.
- Each edge represents a control flow transfer (e.g., function call, method call, class instantiation, conditional execution).
- For each node, include its type (e.g., "function", "method", "class", "main_block", "conditional", "loop").
- For each edge, specify the type of transfer (e.g., "CALL", "METHOD_CALL", "INSTANTIATION", "CONDITIONAL", "LOOP", "EXCEPTION_HANDLER").
- If a function/method is an entry point (like main), include that information for the corresponding node.
- Identify the main entry point(s) of the program.
- Include async functions and their await calls.
- Track exception handling flows (try/except blocks).

PYTHON CODE:
{source_code}

Please return the JSON output only, ensuring it's valid and complete.
The JSON should contain:
{{
  "main_entry_points": ["__main__", "main"],
  "imports": ["module1", "module2"],
  "classes": ["ClassName1", "ClassName2"],
  "flow_graph": [
    {{
      "node": "__main__",
      "type": "main_block",
      "is_entry_point": true,
      "line_number": 1,
      "edges_to": [
        {{"target": "main", "transfer_type": "CALL", "line_number": 5}},
        {{"target": "setup_logging", "transfer_type": "CALL", "line_number": 3}}
      ]
    }},
    {{
      "node": "main",
      "type": "function",
      "is_entry_point": true,
      "async": false,
      "parameters": ["arg1", "arg2"],
      "line_number": 10,
      "edges_to": [
        {{"target": "process_data", "transfer_type": "CALL", "line_number": 15}},
        {{"target": "MyClass", "transfer_type": "INSTANTIATION", "line_number": 20}}
      ]
    }},
    {{
      "node": "MyClass.__init__",
      "type": "method",
      "is_entry_point": false,
      "class_name": "MyClass",
      "line_number": 25,
      "edges_to": [
        {{"target": "self.initialize", "transfer_type": "METHOD_CALL", "line_number": 27}}
      ]
    }}
  ]
}}
"""
}