import re
import json

def safe_extract_json(response_text):
    try:
        json_match = re.search(r'(\{.*\})', response_text, re.DOTALL)
        json_content = json_match.group(1) if json_match else response_text
        return json.loads(json_content)
    except Exception:
        return None


def graph_to_json(response_records, alias):
    """
    Μετατρέπει Neo4j Nodes σε JSON serializable list.
    """
    try:
        document_info = []
        for record in response_records:
            node = record.get(alias)
            if node is None:
                continue

            flat_data = {
                "id": str(node.element_id),         # Χρησιμοποιούμε element_id για μοναδικότητα
                "labels": list(node.labels),
                **node._properties
            }
            document_info.append(flat_data)

        return document_info

    except Exception as e:
        print(f"Error converting graph to JSON: {e}")
        return []


if __name__ == "__main__":
    # Mock Neo4j record for testing
    class MockNode:
        def __init__(self):
            self.response_text = """
<Node element_id='4:e10eaa5e-5305-4615-9d8c-0fdc9adbd5fa:12' labels=frozenset({'Document'}) properties={'filename': 'KICKS', 'language': 'COBOL', 'full_path': 'workspace\\DOGECICS\\CLIST\\KICKS', 'classification': 'Programming Language source file'}>
"""            

    
    
    # Test the function
    mock_response = [MockNode().response_text]
    result = graph_to_json(mock_response, "d")
    print(result)