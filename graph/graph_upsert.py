def upsert_repository(session, repository_name):
    session.run("""
        MERGE (r:Repository {repository_name: $repository_name})
    """, repository_name=repository_name)


def upsert_document(session, repository_name, filename, full_path, language, classification):
    session.run("""
        MATCH (r:Repository {repository_name: $repository_name})
        MERGE (d:Document {filename: $filename})
        SET d.full_path = $full_path,
            d.language = $language,
            d.classification = $classification
        MERGE (r)-[:CONTAINS]->(d)
    """, repository_name=repository_name, filename=filename, full_path=full_path, language=language, classification=classification)


def upsert_entry_point(session, document_filename, name, node_type, is_entry_point):
    session.run("""
        MATCH (d:Document {filename: $document_filename})
        MERGE (e:EntryPoint {name: $name, document: $document_filename})
        SET e.type = $node_type, e.is_entry_point = $is_entry_point
        MERGE (d)-[:FLOWS_TO]->(e)
    """, document_filename=document_filename, name=name, node_type=node_type, is_entry_point=is_entry_point)


def upsert_internal_edge(session, from_entry, to_internal, document_filename, transfer_type):
    session.run("""
        MATCH (e:EntryPoint {name: $from_entry, document: $document_filename})
        MERGE (n:InternalCall {name: $to_internal, document: $document_filename})
        MERGE (e)-[r:OUTBOUND_EDGE]->(n)
        SET r.transfer_type = $transfer_type
        MERGE (n)-[:INBOUND_EDGE]->(e)
    """, from_entry=from_entry, to_internal=to_internal, document_filename=document_filename, transfer_type=transfer_type)


def upsert_external_edge(session, from_entry, target_name, integration_type, document_filename, transfer_type):
    result = session.run("""
        MATCH (d:Document {filename: $target_name})
        RETURN d
    """, target_name=target_name)
    
    if result.single():
        session.run("""
            MATCH (src_doc:Document {filename: $document_filename})
            MATCH (target_doc:Document {filename: $target_name})
            MERGE (src_doc)-[r:INTEGRATES_WITH]->(target_doc)
            SET r.via = $transfer_type, r.integration_type = $integration_type
        """, document_filename=document_filename, target_name=target_name, transfer_type=transfer_type, integration_type=integration_type)
    else:
        session.run("""
            MATCH (e:EntryPoint {name: $from_entry, document: $document_filename})
            MERGE (ext:ExternalCall {target: $target_name, document: $document_filename})
            SET ext.integration_type = $integration_type
            MERGE (e)-[r:OUTBOUND_EDGE]->(ext)
            SET r.transfer_type = $transfer_type
        """, from_entry=from_entry, target_name=target_name, document_filename=document_filename, transfer_type=transfer_type, integration_type=integration_type)
