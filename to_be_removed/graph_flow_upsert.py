from graph.graph_upsert import (
    upsert_document,
    upsert_entry_point,
    upsert_internal_edge,
    upsert_external_edge
)

def process_flow_response(session, repository_name, filename, language, classification, flow_data):
    """
    Παίρνει τα δεδομένα flow του αρχείου και τα εισάγει στο GraphDB με Upserts
    """
    # 1. Upsert το Document
    upsert_document(
        session=session,
        repository_name=repository_name,
        filename=filename,
        full_path=filename,  # Εδώ βάζεις το πλήρες path αν το έχεις αλλού
        language=language,
        classification=classification
    )

    # 2. Εισαγωγή Entry Points και Edges
    flow_graph = flow_data.get("flow_graph", [])
    for node in flow_graph:
        step_name = node["node"]
        is_entry = node.get("is_entry_point", False)
        print(f"step_name: {step_name}, is_entry: {is_entry}")
        upsert_entry_point(
            session=session,
            document_filename=filename,
            name=step_name,
            node_type="paragraph",
            is_entry_point=is_entry
        )
        print(f"node: {node}")
        for edge_data in node.get("edges_to", []):
            target = edge_data["target"]
            transfer_type = edge_data["transfer_type"]
            integration_type = edge_data["integration_type"]
            print(f"target: {target}, transfer_type: {transfer_type}, integration_type: {integration_type}")
            if integration_type == "internal":
                print(f"upsert_internal_edge: {step_name}, {target}, {filename}, {transfer_type}")
                upsert_internal_edge(session, from_entry=step_name, to_internal=target, document_filename=filename, transfer_type=transfer_type)
            else:
                print(f"upsert_external_edge: {step_name}, {target}, {filename}, {transfer_type}, {integration_type}")
                upsert_external_edge(session, from_entry=step_name, target_name=target, integration_type=integration_type, document_filename=filename, transfer_type=transfer_type)
