from graph_db import get_session

# ----------------- Upsert Archimate Elements -----------------

def upsert_technology_system(session, repository_name):
    session.run("""
        MERGE (s:TechnologySystem {name: $repository_name})
    """, repository_name=repository_name)


def upsert_technology_artifact(session, repository_name, filename, full_path, language, classification):
    session.run("""
        MATCH (s:TechnologySystem {name: $repository_name})
        MERGE (a:TechnologyArtifact {filename: $filename, full_path: $full_path})
        SET a.language = $language, a.classification = $classification
        MERGE (s)-[:CONTAINS]->(a)
    """, repository_name=repository_name, filename=filename, full_path=full_path, language=language, classification=classification)


def upsert_technology_function(session, filename, func_name, is_entry=False):
    session.run("""
        MATCH (a:TechnologyArtifact {filename: $filename})
        MERGE (f:TechnologyFunction {name: $func_name, filename: $filename})
        SET f.is_entry_point = $is_entry
        MERGE (a)-[:FLOWS_TO]->(f)
    """, filename=filename, func_name=func_name, is_entry=is_entry)


def upsert_internal_flow(session, source_name, target_name, filename, flow_type="PERFORM"):
    session.run("""
        MATCH (src:TechnologyFunction {name: $source_name, filename: $filename})
        MERGE (tgt:TechnologyFunction {name: $target_name, filename: $filename})
        MERGE (src)-[:FLOWS_TO {flow_type: $flow_type, integration: 'internal'}]->(tgt)
    """, source_name=source_name, target_name=target_name, filename=filename, flow_type=flow_type)


def upsert_external_interaction(session, source_name, target_name, filename, interaction_type):
    session.run("""
        MATCH (src:TechnologyFunction {name: $source_name, filename: $filename})
        MERGE (svc:ApplicationService {name: $target_name})
        MERGE (src)-[:INTERACTS_WITH {interaction_type: $interaction_type}]->(svc)
    """, source_name=source_name, target_name=target_name, filename=filename, interaction_type=interaction_type)

