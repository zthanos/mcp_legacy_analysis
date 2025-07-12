def get_all_repositories(session):
    """
    Retrieves all repositories.

    Args:
        session (neo4j.Session): Active session.

    Returns:
        list[neo4j.Node]: Repository nodes.
    """
    result = session.run("""
        MATCH (r:Repository)
        RETURN r
    """)
    return [record["r"] for record in result]


def get_documents_by_repository(session, repository_name):
    """
    Retrieves all documents in a repository.

    Args:
        session (neo4j.Session): Active session.
        repository_name (str): Repository name.

    Returns:
        list[neo4j.Node]: Document nodes.
    """
    result = session.run("""
        MATCH (r:Repository {repository_name: $repository_name})-[:CONTAINS]->(d:Document)
        RETURN d
    """, repository_name=repository_name)
    return [record["d"] for record in result]


def get_documents_analysis(session, repository_name):
    """
    Retrieves filenames and analyses for documents in a repository.

    Args:
        session (neo4j.Session): Active session.
        repository_name (str): Repository name.

    Returns:
        list[dict]: Filenames and analysis data.
    """
    result = session.run("""
        MATCH (r:Repository {repository_name: $repository_name})-[:CONTAINS]->(d:Document)
        RETURN d.filename AS filename, d.analysis AS analysis
    """, repository_name=repository_name)
    return [{"filename": record["filename"], "analysis": record["analysis"]} for record in result]


def get_document_details(session, filename):
    """
    Retrieves document details by filename.

    Args:
        session (neo4j.Session): Active session.
        filename (str): Document filename.

    Returns:
        neo4j.Node | None: Document node or None.
    """
    result = session.run("""
        MATCH (d:Document {filename: $filename})
        RETURN d
    """, filename=filename)
    record = result.single()
    return record["d"] if record else None


def get_document_flow(session, filename):
    """
    Retrieves entry points and flow (internal, external) for a document.

    Args:
        session (neo4j.Session): Active session.
        filename (str): Document filename.

    Returns:
        list[dict]: Flow paths.
    """
    result = session.run("""
        MATCH (d:Document {filename: $filename})-[:FLOWS_TO]->(e:EntryPoint)
        OPTIONAL MATCH path = (e)-[:OUTBOUND_EDGE*]->(target)
        RETURN d, e, path
    """, filename=filename)
    return result.data()


def get_cross_document_integrations(session, filename):
    """
    Retrieves cross-document integration relationships.

    Args:
        session (neo4j.Session): Active session.
        filename (str): Document filename.

    Returns:
        list[dict]: Integration paths.
    """
    result = session.run("""
        MATCH (src:Document {filename: $filename})-[:INTEGRATES_WITH]->(target:Document)
        RETURN src, target
    """, filename=filename)
    return result.data()
