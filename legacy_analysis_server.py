from fastmcp import FastMCP, Context
from pathlib import Path
from graph_db import get_session, get_driver
from tools.repository import (
    execute_fetch_repository, 
    get_repository_summary,
    execute_classify_repository
)

from tools.workspace import execute_expose_workspace
from tools.document import (
    retrieve_document_info,
    classify_document,
    get_document_content,
    get_documents_by_repository,
    document_analysis,
)
from prompts.code_analysis_prompt import get_code_analysis_prompt

mcp = FastMCP(name="legacy-analyzer-v1")
driver = get_driver()
session = get_session(driver)

WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

_repo_registry = {}  # Tracks repository aliases and paths


def extract_alias_from_url(repo_url: str) -> str:
    """
    Extracts a short alias from the repository URL.

    Args:
        repo_url (str): Full URL of the repository.

    Returns:
        str: Alias derived from the URL.
    """
    return Path(repo_url.rstrip("/").split("/")[-1]).stem


# ─── Exposed MCP Tools ──────────────────────────────────────────────────────────

@mcp.tool(
    name="fetch_repository",
    description="Clones a repository (e.g., COBOL) and registers it as a resource.",
)
async def fetch_repository(repo_url: str, ctx: Context) -> str:
    """
    Fetches and registers a repository.

    Args:
        repo_url (str): Repository URL.
        ctx (Context): MCP execution context.

    Returns:
        str: Status message.
    """
    return await execute_fetch_repository(session=session, ctx=ctx, repo_url=repo_url)


@mcp.tool(
    name="classify_repository",
    description="Analyzes and classifies files in a repository by programming language or file type.",
)
async def classify_repository(repository_name: str, ctx: Context) -> str:
    """
    Classifies files within a repository.

    Args:
        repository_name (str): Repository alias.
        ctx (Context): MCP execution context.

    Returns:
        str: Classification results.
    """
    await ctx.info(f"Classifying repository '{repository_name}'")
    try:
        return await execute_classify_repository(
            session=session, ctx=ctx, repository_name=repository_name
        )
    except Exception as ex:
        await ctx.error(f"Error while classifying repository: {ex}")
        return "Classification failed."


@mcp.tool(
    name="summarize_repository_scope",
    description="Generates a high-level summary of the repository content and purpose.",
)
async def summarize_repository_scope(repository_name: str, ctx: Context) -> str:
    """
    Summarizes repository content.

    Args:
        repository_name (str): Repository alias.
        ctx (Context): MCP execution context.

    Returns:
        str: Repository summary.
    """
    await ctx.info(f"Retrieving summary for repository '{repository_name}'")
    data = await get_repository_summary(session, repository_name)
    size_kb = len(str(data).encode('utf-8')) / 1024
    await ctx.debug(f"Summary size: {size_kb:.2f} KB")
    return str(data)


@mcp.tool(
    name="get_document_info",
    description="Retrieves metadata and attributes of a specific document.",
)
async def get_document_info(repository: str, filename: str, ctx: Context) -> list[dict]:
    """
    Retrieves document information.

    Args:
        repository (str): Repository alias.
        filename (str): Document name.
        ctx (Context): MCP execution context.

    Returns:
        list[dict]: Document metadata.
    """
    return retrieve_document_info(
        session=session, repository=repository, filename=filename
    )


@mcp.tool(
    name="list_workspace_files",
    description="Lists all file names currently stored in the workspace.",
)
def list_workspace_files(ctx: Context) -> list[str]:
    """
    Lists workspace files.

    Args:
        ctx (Context): MCP execution context.

    Returns:
        list[str]: Filenames in workspace.
    """
    results = execute_expose_workspace(ctx)
    return results or []


@mcp.tool(
    name="classify_document_content",
    description="Classifies the content of a document by programming language or type.",
)
async def classify_document_content(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Classifies a document's content.

    Args:
        repository_name (str): Repository alias.
        filename (str): Document name.
        ctx (Context): MCP execution context.

    Returns:
        str: Classification result.
    """
    response =  await classify_document(
        session=session, repository=repository_name, filename=filename, ctx=ctx
    )
    if response:
        return response
    return "Unable to Classify Document"


@mcp.tool(
    name="retrieve_document_content",
    description="Retrieves the full text content of a document from the repository.",
)
async def retrieve_document_content(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Retrieves document content.

    Args:
        repository_name (str): Repository alias.
        filename (str): Document name.
        ctx (Context): MCP execution context.

    Returns:
        str: Document content.
    """
    return await get_document_content(
        session=session, repository=repository_name, filename=filename, ctx=ctx
    )


@mcp.tool(
    name="analyze_document",
    description="Performs static analysis on a document and returns a structured JSON result.",
)
async def analyze_document(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Analyzes a document and returns analysis results.

    Args:
        repository_name (str): Repository alias.
        filename (str): Document name.
        ctx (Context): MCP execution context.

    Returns:
        str: Analysis data in JSON format.
    """
    return await document_analysis(
        session=session,
        repository_name=repository_name,
        filename=filename,
        ctx=ctx,
    )


# ─── Exposed Prompts ───────────────────────────────────────────────────────────

@mcp.prompt(
    name="code_analysis_prompt",
    description="Generates a system-level prompt for extracting code execution flow and dependencies.",
)
async def generate_code_analysis_prompt(filename: str, repository_name: str, ctx: Context) -> str:
    """
    Generates a language-aware code analysis prompt.

    Args:
        filename (str): Document name.
        repository_name (str): Repository alias.
        ctx (Context): MCP execution context.

    Returns:
        str: Prepared prompt string.
    """
    return get_code_analysis_prompt(filename, repository_name)
