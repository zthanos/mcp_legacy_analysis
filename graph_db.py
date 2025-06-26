from neo4j import GraphDatabase
import os


def get_driver():
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not uri or not username or not password:
        raise ValueError("Missing required Neo4j environment variables")
    
    return GraphDatabase.driver(uri, auth=(username, password))

def get_session(driver):
    database = os.getenv("NEO4J_DATABASE")
    if not database:
        raise ValueError("Missing required NEO4J_DATABASE environment variable")
    return driver.session(database=database)

# ----------------- Συναρτήσεις MCP -----------------

def insert_repository(session, repository_name, full_path, filename, language, classification):
    """Δημιουργεί ή ενημερώνει ένα Repository node"""
    session.run("""
        MERGE (r:Repository {repository_name: $repository_name, filename: $filename})
        SET r.full_path = $full_path,
            r.language = $language,
            r.classification = $classification
    """, repository_name=repository_name, full_path=full_path, filename=filename, language=language, classification=classification)


def insert_field(session, repository_name, filename, name, type_, size, sudoType):
    """Συνδέει Field node με Repository"""
    session.run("""
        MATCH (r:Repository {repository_name: $repository_name, filename: $filename})
        CREATE (f:Field {name: $name, type: $type, size: $size, sudoType: $sudoType})
        CREATE (r)-[:HAS_FIELD]->(f)
    """, repository_name=repository_name, filename=filename, name=name, type=type_, size=size, sudoType=sudoType)


def get_all_repositories(session):
    """Λίστα όλων των Repositories"""

    result = session.run("MATCH (r:Repository) RETURN r")
    return [record["r"] for record in result]


def get_repository(session, repository_name):
    """Επιστροφή Repository με βάση το όνομα"""

    result = session.run("MATCH (r:Repository {repository_name: $repository_name}) RETURN r", repository_name=repository_name)
    return [record["r"] for record in result]


def get_repository_by_filename(session, filename):
    """Αναζήτηση με βάση filename"""

    result = session.run("MATCH (r:Repository {filename: $filename}) RETURN r", filename=filename)
    return [record["r"] for record in result]


def get_repository_by_classification(session, classification, repository_name):
    """Αναζήτηση με βάση classification και repository"""

    result = session.run("""
        MATCH (r:Repository {repository_name: $repository_name, classification: $classification})
        RETURN r
    """, repository_name=repository_name, classification=classification)
    return [record["r"] for record in result]


def get_file_full_path(session, repository_name, filename):
    """Λήψη του full_path ενός αρχείου"""

    result = session.run("""
        MATCH (r:Repository {repository_name: $repository_name, filename: $filename})
        RETURN r.full_path AS path
    """, repository_name=repository_name, filename=filename)
    
    record = result.single()
    return record["path"] if record else None


def close_driver(session):
    """Κλείσιμο της σύνδεσης"""
    session.driver.close()
