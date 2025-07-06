from fastmcp import FastMCP, Context
from pathlib import Path
from graph_db import get_session, get_driver, get_repository
from tools.fetch_repository import execute_fetch_repository
from tools.classify_repository import execute_classify_repository
from tools.expose_workspace import execute_expose_workspace
from tools.extract_document_flow import extract_document_flow
from tools.document import retreive_document_info, classify_document, get_file_content
from tools.extract_document_flow import extract_language_specific_flow as extract_language_specific_flow_tool, extract_flow_with_specific_prompt
from templates.code_analyzer_prompt_generator import flow_extraction

mcp = FastMCP(name="legacy-analyzer-v1")
driver = get_driver()
session = get_session(driver)


WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

_repo_registry = {}  # Keeps track of aliases and paths


def extract_alias_from_url(repo_url: str) -> str:
    return Path(repo_url.rstrip("/").split("/")[-1]).stem


@mcp.tool(name="fetch_repository", description="Clones a COBOL repository and registers it as a resource.")
async def fetch_repository(repo_url: str, ctx: Context) -> str:
    return await execute_fetch_repository(session=session, ctx=ctx, repo_url=repo_url)  

@mcp.tool(name="classify_repository", description="Classifies files in a repository by programming language or file type.")
async def classify_repository(repository_name: str, ctx: Context) -> str:
    return await execute_classify_repository(session=session, ctx=ctx, repository_name=repository_name)

@mcp.tool(name="processed_repository", description="Returns a list of file from a processed repository by name.")
async def processed_repository(repository: str, ctx: Context) -> list[dict]:
    files_in_repository = get_repository(session=session, repository_name=repository)
    print(f"files_in_repository: {files_in_repository}")
    return files_in_repository



@mcp.tool(name="extract_flow", description="Extracts the execution flow of a program, starting from its primary entry point, and returns it in a structured JSON format.")
async def extract_flow(repository: str, filename: str, ctx: Context) -> str:
    await ctx.info(f"Extracting flow for {filename} in {repository}")
    document_info = retreive_document_info(session=session, repository=repository, filename=filename)
    print(f"document_info: {document_info}")
    if len(document_info) == 0:
        return "No document info found"
    analyzed_data =  await extract_document_flow(
        mcp=mcp,
        repository=repository,
        filename=document_info[0]["full_path"],
        classification=document_info[0]["language"],
        ctx=ctx,
    )    
    print(f"analyzed_data: {analyzed_data}")
    return analyzed_data



@mcp.tool(name="get_map_files", description="Returns a list of map files from a processed repository by name.")
async def get_map_files(repository: str, ctx: Context) -> str:
    # response = get_repository_by_classification("BMS Map", repository)
    # await ctx.info(f"Analyzing {len(response)} map files...")
    # analyzed_data = await analyze_map("workspace\\DOGECICS\\BMS\\DOGEDMAP", ctx)
    analyzed_data =  await extract_document_flow(
        mcp=mcp,
        repository=repository,
        filename="workspace\\DOGECICS\\COBOL\\DOGEMAIN",
        classification="COBOL",
        ctx=ctx,
    )    
    print(f"analyzed_data: {analyzed_data}")
    # maps_data = json.loads(response)
    # for map in maps_data:
    #    analyzed_data = await analyze_map(map, ctx) 

    return analyzed_data


@mcp.tool(name="find_copy_definition", description="Searches all files for a COBOL COPY label (e.g. DOGEDT) and returns the first file that contains it.")
def find_copy_definition(ctx: Context, resource_uri: str, copy_name: str) -> dict:
    import re
    # ctx.log.info(f"Searching for COPY definition: {copy_name} in {resource_uri}")
    repo_alias = resource_uri.replace("resource://", "")
    base_path = WORKSPACE / repo_alias

    matched_files = []

    # Traverse all files like list_cobol_files does
    for file_path in base_path.rglob("*"):
        # ctx.log.info(f"Checking file: {file_path}")
        if not file_path.is_file():
            continue
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
               for line in f:
                    # Look for a line that starts with the copy_name (label-style)
                    if re.match(rf"^\s*{re.escape(copy_name)}\b", line):
                        matched_files.append({
                            "copy_name": copy_name,
                            "path": str(file_path.relative_to(base_path)),
                            "line": line.strip()
                        })
                        break  # stop after first match in file
        except Exception:
            continue  # skip unreadable files

    if matched_files:
        return {
            "status": "found",
            "matches": matched_files
        }
    else:
        return {
            "status": "not_found",
            "message": f"No definition for '{copy_name}' found."
        }


@mcp.tool(name="get_document_info", description="Returns the information of a document.")
async def get_document_info(repository: str, filename: str, ctx: Context) -> list[dict]:
    document_info = retreive_document_info(session=session, repository=repository, filename=filename)
    print(f"document_info: {document_info}")
    return document_info

@mcp.tool(name="return_workspace", description="Returns the workspace file names.")
def return_workspace(ctx: Context) -> list[str]:
    results = execute_expose_workspace(ctx)
    if results is None:
        return []
    return results


@mcp.tool("file_classification", description="Classifies file content by programming language or file type.")
async def file_classification(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Classifies a file based on its content and filename.
    Takes filename and content as input to avoid file system operations.
    Returns programming language or file type classification.
    """

    classification = await classify_document(session=session, repository=repository_name, filename=filename, ctx=ctx)
    return classification

@mcp.tool("retrieve_file_content", description="Retrieves the content of a file from the repository.")
async def retrieve_file_content(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Retrieves file content from the repository.
    Handles various file encodings and provides detailed error information.
    Returns just the file content for use by other tools.
    """
    return await get_file_content(session=session, repository=repository_name, filename=filename, ctx=ctx)

@mcp.tool("get_language_specific_prompt", description="Returns the language-specific prompt for the given language.")
async def get_language_specific_prompt(language: str, source_code: str, repository_name: str, filename: str, ctx: Context) -> dict:
    system_prompt, llm_prompt = flow_extraction(
        source_code=source_code,
        filename=filename,
        repository_name=repository_name,
        program_id=filename,
        language=language
    )

    return {
        "system_prompt": system_prompt,
        "llm_prompt": llm_prompt
    }    
    
@mcp.tool("extract_flow_with_specific_prompt", description="Extracts the execution flow of a program, starting from its primary entry point, and returns it in a structured JSON format.")
async def extract_flow_with_prepared_prompt(system_prompt: str, llm_prompt: str, ctx: Context) -> str:
    return await extract_flow_with_specific_prompt(mcp=mcp, llm_prompt=llm_prompt, system_prompt=system_prompt, ctx=ctx)


@mcp.tool("extract_language_specific_flow", description="Extracts the execution flow of a program, starting from its primary entry point, and returns it in a structured JSON format.")
async def extract_language_specific_flow(language: str, source_code: str, repository_name: str, filename: str, ctx: Context) -> str:
    return await extract_language_specific_flow_tool(mcp=mcp, language=language, source_code=source_code, repository_name=repository_name, filename=filename, ctx=ctx)


@mcp.prompt(name="MCP_Server_Language-Aware_Code_Analysis_Prompt", description="Extracts the execution flow and external dependencies of any supported source code.")
async def extract_code_flow(filename: str, repository_name: str, ctx: Context) -> str:
    """
    System-Level Prompt for MCP Server to perform language-aware static code analysis.
    """

    return f"""
# MCP Server Language-Aware Code Analysis Prompt

## System Instructions

You are a language-agnostic static code analyzer operating within the MCP Server.

### Analysis Workflow

1. **Identify Programming Language**
   - Use the tool `get_document_info` with repository: `{repository_name}`, filename: `{filename}`
   - This returns metadata including detected language (e.g., Python, COBOL, CLIST, C)

2. **Retrieve Source Code**
   - Use `retrieve_file_content` with `{repository_name}` and `{filename}`
   - Assign the result to `source_code`

3. **Language-Specific Analysis**
   - Based on the detected language, invoke `get_language_specific_prompt(language, source_code, filename, repository_name)`
   - Use the returned prompt template for that language to perform in-depth static analysis

4. **Produce JSON Output**
   - Output strictly valid JSON as per the language-agnostic schema:
   
```json
{{
  "program_id": "unique program/module identifier",
  "filename": "{filename}",
  "language": "detected language",
  "main_entry_points": ["entry points list"],
  "flow_graph": [...],
  "path_to_critical": [...]
}}
"""