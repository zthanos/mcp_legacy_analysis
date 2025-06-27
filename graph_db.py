from neo4j import GraphDatabase
import os

# ----------------- Σύνδεση -----------------

def get_driver():
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not uri or not username or not password:
        raise ValueError("Missing required Neo4j connection info")
    
    return GraphDatabase.driver(uri, auth=(username, password))


def get_session(driver):
    database = os.getenv("NEO4J_DATABASE")
    if not database:
        raise ValueError("Missing required NEO4J_DATABASE")
    return driver.session(database=database)

# ----------------- Βοηθητικά -----------------

def node_to_dict(node):
    return {
        "id": node.id,
        "labels": list(node.labels),
        **node._properties
    }

# ----------------- Repositories -----------------


def insert_repository(session, repository_name):
    session.run("""
        MERGE (r:Repository {repository_name: $repository_name})
    """, repository_name=repository_name)


def insert_document(session, repository_name, full_path, filename, language, classification):
    session.run("""
        MERGE (r:Repository {repository_name: $repository_name, filename: $filename})
        SET r.full_path = $full_path,
            r.language = $language,
            r.classification = $classification
    """, repository_name=repository_name, full_path=full_path, filename=filename, language=language, classification=classification)



def insert_field(session, repository_name, filename, name, type_, size, sudoType):
    session.run("""
        MATCH (r:Repository {repository_name: $repository_name, filename: $filename})
        CREATE (f:Field {name: $name, type: $type, size: $size, sudoType: $sudoType})
        CREATE (r)-[:HAS_FIELD]->(f)
    """, repository_name=repository_name, filename=filename, name=name, type=type_, size=size, sudoType=sudoType)


def get_all_repositories(session):
    result = session.run("MATCH (r:Repository) RETURN r")
    return [node_to_dict(record["r"]) for record in result]


def get_repository(session, repository_name):
    result = session.run("MATCH (r:Repository {repository_name: $repository_name}) RETURN r", repository_name=repository_name)
    return [node_to_dict(record["r"]) for record in result]


def get_repository_by_filename(session, filename):
    result = session.run("MATCH (r:Repository {filename: $filename}) RETURN r", filename=filename)
    return [node_to_dict(record["r"]) for record in result]


def get_repository_by_classification(session, classification, repository_name):
    result = session.run("""
        MATCH (r:Repository {repository_name: $repository_name, classification: $classification})
        RETURN r
    """, repository_name=repository_name, classification=classification)
    return [node_to_dict(record["r"]) for record in result]


def get_file_full_path(session, repository_name, filename):
    result = session.run("""
        MATCH (r:Repository {repository_name: $repository_name, filename: $filename})
        RETURN r.full_path AS path
    """, repository_name=repository_name, filename=filename)
    
    record = result.single()
    return record["path"] if record else None

# ----------------- Flow Graph -----------------

def insert_flow_node(session, filename, node_name, node_type, is_entry_point):
    label = "Program" if node_type == "program" else "Paragraph"
    
    session.run(f"""
        MERGE (n:{label} {{name: $node_name, filename: $filename}})
        SET n.is_entry_point = $is_entry_point
    """, node_name=node_name, filename=filename, is_entry_point=is_entry_point)


def insert_flow_edge(session, src_name, tgt_name, filename, transfer_type, integration_type):
    session.run("""
        MATCH (src {name: $src_name, filename: $filename})
        MERGE (tgt {name: $tgt_name})
        MERGE (src)-[r:CONTROL_FLOW {
            transfer_type: $transfer_type,
            integration_type: $integration_type
        }]->(tgt)
    """, src_name=src_name, tgt_name=tgt_name, filename=filename, transfer_type=transfer_type, integration_type=integration_type)



def insert_flow_graph(session, analyzed_data):
    filename = analyzed_data["filename"]
    
    for node in analyzed_data["flow_graph"]:
        insert_flow_node(session, filename, node["node"], node["type"], node["is_entry_point"])
        
        for edge in node.get("edges_to", []):
            integration_type = edge.get("integration_type", "internal")  # default αν λείπει
            insert_flow_edge(
                session,
                src_name=node["node"],
                tgt_name=edge["target"],
                filename=filename,
                transfer_type=edge["transfer_type"],
                integration_type=integration_type
            )
