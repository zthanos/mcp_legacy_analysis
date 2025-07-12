from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

def get_driver():
    """
    Initializes a Neo4j driver instance using environment variables.

    Returns:
        neo4j.Driver: Active Neo4j driver.
    """
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")

    if not uri or not username or not password:
        raise ValueError("Missing required Neo4j connection info")

    return GraphDatabase.driver(uri, auth=(username, password))


def get_session(driver):
    """
    Creates a Neo4j session for a specific database.

    Args:
        driver (neo4j.Driver): Neo4j driver.

    Returns:
        neo4j.Session: Active session.
    """
    database = os.getenv("NEO4J_DATABASE")
    if not database:
        raise ValueError("Missing required NEO4J_DATABASE")

    return driver.session(database=database)


def node_to_dict(node):
    """
    Converts a Neo4j node to a dictionary.

    Args:
        node (neo4j.Node): Neo4j node.

    Returns:
        dict: Node properties with ID and labels.
    """
    return {
        "id": node.id,
        "labels": list(node.labels),
        **node._properties
    }


def get_repository(session, repository_name):
    """
    Retrieves a repository node by name.

    Args:
        session (neo4j.Session): Active session.
        repository_name (str): Repository name.

    Returns:
        list[dict]: List of repository nodes.
    """
    result = session.run(
        "MATCH (r:Repository {repository_name: $repository_name}) RETURN r",
        repository_name=repository_name
    )
    return [node_to_dict(record["r"]) for record in result]
