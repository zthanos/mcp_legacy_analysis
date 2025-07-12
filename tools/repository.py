from utils.utils import classify_by_extension, safe_read_file
import subprocess
import re
from pathlib import Path
from graph.graph_upsert import upsert_repository, upsert_document
from graph.graph_query import get_documents_analysis
from tools.document import document_analysis
from tools.workspace import WORKSPACE


WORKSPACE.mkdir(exist_ok=True)


def extract_alias_from_url(repo_url: str) -> str:
    """
    Extracts alias name from repository URL.
    """
    return Path(repo_url.rstrip("/").split("/")[-1]).stem


async def execute_fetch_repository(session, ctx, repo_url: str) -> str:
    """
    Clones repository if not present locally and upserts it in the graph DB.

    Args:
        session: Neo4j session.
        ctx: MCP context.
        repo_url (str): Git repository URL.

    Returns:
        str: Repository alias name.
    """
    repository_name = extract_alias_from_url(repo_url)
    repo_path = WORKSPACE / repository_name

    if repo_path.exists():
        await ctx.info(f"Repository '{repository_name}' already exists locally.")
    else:
        await ctx.info(f"Cloning repository '{repository_name}'...")
        subprocess.run(["git", "clone", repo_url, str(repo_path)], check=True)

    upsert_repository(session, repository_name)
    return repository_name


async def execute_classify_repository(session, ctx, repository_name: str) -> str:
    """
    Classifies all files in a repository by type and performs analysis.

    Args:
        session: Neo4j session.
        ctx: MCP context.
        repository_name (str): Repository alias.

    Returns:
        str: Repository name after classification.
    """
    repo_path = WORKSPACE / repository_name
    await ctx.info(f"Starting file classification for repository '{repository_name}'...")

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file() or ".git" in file_path.parts:
            continue

        file_type, language, classification = classify_by_extension(file_path)

        if file_type == "skip":
            await _register_document(session, repository_name, file_path, language, classification, "")
            continue

        content, encoding_used = safe_read_file(file_path)
        if not content:
            await ctx.warning(f"Skipping unreadable file: {file_path}")
            continue

        try:
            await ctx.info(f"Analyzing document: {file_path.name}")
            analysis_data = await document_analysis(session, repository_name, file_path.name, ctx)
            await _register_document(session, repository_name, file_path, language, classification, analysis_data)
        except Exception as e:
            await ctx.error(f"Error classifying file {file_path}: {e}")

    return repository_name


async def get_repository_summary(session, repository_name: str):
    """
    Retrieves analysis summary for all documents in a repository.

    Args:
        session: Neo4j session.
        repository_name (str): Repository alias.

    Returns:
        list[dict]: List of analysis data per document.
    """
    return get_documents_analysis(session, repository_name)


# ----------------- Helper Functions -----------------

async def _register_document(session, repository_name, file_path, language, classification, analysis_data):
    upsert_document(
        session=session,
        repository_name=repository_name,
        full_path=str(file_path),
        filename=str(file_path.name),
        language=language,
        classification=classification,
        analysis=analysis_data,
    )
