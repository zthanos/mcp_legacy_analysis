from helpers.response_helper import graph_to_json

def get_all_repositories(session):
    result = session.run("""
        MATCH (r:Repository)
        RETURN r
    """)
    return [record["r"] for record in result]


def get_documents_by_repository(session, repository_name):
    print(f"MATCH (r:Repository {{repository_name: ${repository_name}}})-[:CONTAINS]->(d:Document) ")
    result = session.run("""
        MATCH (r:Repository {repository_name: $repository_name})-[:CONTAINS]->(d:Document)
        RETURN d
    """, repository_name=repository_name)
    return [record["d"] for record in result]


def get_document_details(session, filename):
    result = session.run("""
        MATCH (d:Document {filename: $filename})
        RETURN d
    """, filename=filename)
    record = result.single()
    return record["d"] if record else None


def get_document_flow(session, filename):
    """
    Επιστρέφει το EntryPoint και όλες τις ροές προς Internal και External Calls για το αρχείο
    """
    result = session.run("""
        MATCH (d:Document {filename: $filename})-[:FLOWS_TO]->(e:EntryPoint)
        OPTIONAL MATCH path = (e)-[:OUTBOUND_EDGE*]->(target)
        RETURN d, e, path
    """, filename=filename)
    return result.data()


def get_cross_document_integrations(session, filename):
    """
    Επιστρέφει τις INTEGRATES_WITH σχέσεις του αρχείου προς άλλα Documents
    """
    result = session.run("""
        MATCH (src:Document {filename: $filename})-[:INTEGRATES_WITH]->(target:Document)
        RETURN src, target
    """, filename=filename)
    return result.data()
