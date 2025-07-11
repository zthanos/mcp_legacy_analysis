from fastmcp import FastMCP, Context
from pathlib import Path
from graph_db import get_session, get_driver
from helpers import response_helper
from tools.fetch_repository import execute_fetch_repository
from tools.classify_repository import execute_classify_repository
from tools.expose_workspace import execute_expose_workspace
from tools.document import (
    retreive_document_info,
    classify_document,
    get_document_content,
    get_documents_by_repository,
    document_analysis
)
# from tools.extract_document_flow import (
#     extract_language_specific_flow as extract_language_specific_flow_tool,
#     extract_flow_with_specific_prompt,
# )
from prompts.code_analysis_prompt import get_code_analysis_prompt

mcp = FastMCP(name="legacy-analyzer-v1")
driver = get_driver()
session = get_session(driver)


WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

_repo_registry = {}  # Keeps track of aliases and paths


def extract_alias_from_url(repo_url: str) -> str:
    return Path(repo_url.rstrip("/").split("/")[-1]).stem


# Exposing Tools


@mcp.tool(
    name="fetch_repository",
    description="Clones a COBOL repository and registers it as a resource.",
)
async def fetch_repository(repo_url: str, ctx: Context) -> str:
    return await execute_fetch_repository(session=session, ctx=ctx, repo_url=repo_url)


@mcp.tool(
    name="classify_repository",
    description="Classifies files in a repository by programming language or file type.",
)
async def classify_repository(repository_name: str, ctx: Context) -> str:
    await ctx.info(f"Classifing repository {repository_name}")
    response = ""
    try:
        response = await execute_classify_repository(
            session=session, ctx=ctx, repository_name=repository_name
        )
    except Exception as ex:
        await ctx.error(f"Error while classifying repository \n{ex}")
    return response


@mcp.tool(
    name="summarize_repository_scope",
    description="Summarizes the purpose of the repository",
)
async def summarize_repository_scope(repository_name: str, ctx: Context):
    await ctx.info(f"Retrieving documents from repository {repository_name}")
    data = get_documents_by_repository(session, repository_name)
    print(data)
    return data


@mcp.tool(
    name="get_document_info", description="Returns the information of a document."
)
async def get_document_info(repository: str, filename: str, ctx: Context) -> list[dict]:
    document_info = retreive_document_info(
        session=session, repository=repository, filename=filename
    )
    print(f"document_info: {document_info}")
    return document_info


@mcp.tool(name="return_workspace", description="Returns the workspace file names.")
def return_workspace(ctx: Context) -> list[str]:
    results = execute_expose_workspace(ctx)
    if results is None:
        return []
    return results


@mcp.tool(
    "document_classification",
    description="Classifies file content by programming language or file type.",
)
async def ducument_classification(
    repository_name: str, filename: str, ctx: Context
) :
    """
    Classifies a document based on its content and filename.
    Takes filename and content as input to avoid file system operations.
    Returns programming language or file type classification.
    """

    classification = await classify_document(
        session=session, repository=repository_name, filename=filename, ctx=ctx
    )
    return classification


@mcp.tool(
    "retrieve_document_content",
    description="Retrieves the content of a file from the repository.",
)
async def retrieve_document_content(
    repository_name: str, filename: str, ctx: Context
) -> str:
    """
    Retrieves file content from the repository.
    Handles various file encodings and provides detailed error information.
    Returns just the file content for use by other tools.
    """
    return await get_document_content(
        session=session, repository=repository_name, filename=filename, ctx=ctx
    )


@mcp.tool("analyze_document",
    description="Performs documnt analysis, and returns it in a structured JSON format.",
)

async def analyze_document(repository_name, filename: str, ctx: Context) -> str:
        analysis_data = await document_analysis(
                session=session,
                repository_name=repository_name,
                filename=filename,
                ctx=ctx
            )
        return analysis_data


# @mcp.tool(
#     "extract_language_specific_flow",
#     description="Extracts the execution flow of a program, starting from its primary entry point, and returns it in a structured JSON format.",
# )
# async def extract_language_specific_flow(
#     language: str, source_code: str, repository_name: str, filename: str, ctx: Context
# ) -> str:
#     return await extract_language_specific_flow_tool(
#         mcp=mcp,
#         language=language,
#         source_code=source_code,
#         repository_name=repository_name,
#         filename=filename,
#         ctx=ctx,
#     )


# Exposing Prompts


@mcp.prompt(
    name="MCP_Server_Language-Aware_Code_Analysis_Prompt",
    description="Extracts the execution flow and external dependencies of any supported source code.",
)
async def extract_code_flow(filename: str, repository_name: str, ctx: Context) -> str:
    """
    System-Level Prompt for MCP Server to perform language-aware static code analysis.
    """
    return get_code_analysis_prompt(filename, repository_name)
