from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

# ----------------- Σύνδεση -----------------

def get_driver():
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    print(uri, username, password)
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

def get_repository(session, repository_name):
    result = session.run("MATCH (r:Repository {repository_name: $repository_name}) RETURN r", repository_name=repository_name)
    return [node_to_dict(record["r"]) for record in result]
