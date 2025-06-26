from fastmcp import FastMCP, Context
from pathlib import Path
from analysis import *
from fastmcp.resources import TextResource
from pydantic import AnyUrl
from data_structure import cobol_data_structure
from flow_analysis import get_file_flow
import subprocess
import os
import json
import git
import re
import sqlite3
from database import  *
import json
from cobol_analysis import extract_edges
from graph_db import get_session, get_driver
from tools.fetch_repository import execute_fetch_repository

# Create MCP Server
mcp = FastMCP(name="Legacy Code Analysis Service")
driver = get_driver()
session = get_session(driver)


WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

_repo_registry = {}  # Keeps track of aliases and paths
init_database()
def extract_alias_from_url(repo_url: str) -> str:
    return Path(repo_url.rstrip("/").split("/")[-1]).stem


@mcp.tool(name="fetch_repository", description="Clones a COBOL repository and registers it as a resource.")
async def fetch_repository(repo_url: str, ctx: Context) -> str:
    return await execute_fetch_repository(session=session, ctx=ctx, repo_url=repo_url)  

    # Register the alias as MCP resource
    @mcp.resource(f"resource://{alias}")
    def repo_root() -> str:
        return str(repo_path)

    
    await ctx.info(f"Starting file classification for repository {alias}...")
    for file_path in repo_path.rglob("*"):
        if file_path.is_file():

            if ".git" in file_path.parts:
                continue
            if file_path.suffix == ".md":
                print(f"Skipping markdown file: {file_path}")
                insert_repository(alias, str(file_path),str(file_path.name), "Text", "Markdown")
                continue
            if file_path.suffix == ".ans":
                print(f"Skipping ansi file: {file_path}")
                insert_repository(alias, str(file_path),str(file_path.name), file_path.suffix.lower(), "ANSI")
                continue                
            image_suffixes = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".ico", ".webp"]
            if file_path.suffix.lower() in image_suffixes:
                print(f"Skipping image file: {file_path}")
                insert_repository(alias, str(file_path), str(file_path.name), file_path.suffix.lower(), "image")
                continue                

            print(f"Processing file: {file_path}")
            relative_path = file_path.relative_to(repo_path)
            content = ""
            encoding_used = ""
            for encoding in ['utf-8', 'cp1252', 'iso-8859-1', 'cp037']:  # cp037 for EBCDIC
                try:
                    with open(file_path, "r", encoding=encoding, errors="replace") as f:
                        content = f.read()
                        encoding_used = encoding
                        break
                except (UnicodeDecodeError, UnicodeError):
                    encoding_used = None
                    continue
            try:
                if encoding_used:
                    classification_json = await classify_file(content, str(file_path.name), alias, ctx)
                    matches = re.findall(r"```json\s*(\{.*?\})\s*```", classification_json, re.DOTALL)
                    extracted_json = matches[0]
                    json_data = json.loads(extracted_json)
                    language = json_data.get("language", "Unknown")
                    classification = json_data.get("classification", "Unknown")
                    print(f"language: {language} classification: {classification} encoding_used: {encoding_used}")
                    insert_repository(alias, str(file_path),str(file_path.name), language, classification)
            except Exception as e:
                print(f"Error classifying file {file_path}: {e}")
                
    return alias

@mcp.tool(name="get_map_files", description="Returns a list of map files from a processed repository by name.")
async def get_map_files(repository: str, ctx: Context) -> list[dict]:
    response = get_repository_by_classification("BMS Map", repository)
    await ctx.info(f"Analyzing {len(response)} map files...")
    analyzed_data = await analyze_map("workspace\\DOGECICS\\BMS\\DOGEDMAP", ctx)
    print(f"analyzed_data: {analyzed_data}")
    # maps_data = json.loads(response)
    # for map in maps_data:
    #    analyzed_data = await analyze_map(map, ctx) 

    return response

@mcp.tool(name="processed_repository", description="Returns a list of file from a processed repository by name.")
async def processed_repository(repository: str, ctx: Context) -> list[dict]:
    files_in_repository = get_repository(repository)
    return files_in_repository
    
@mcp.tool(name="extract_data_structure", description="Extracts COBOL data structures from a file inside a registered resource.")
async def get_data_structure(repository: str, filename: str, ctx: Context) -> str:
    return await cobol_data_structure(mcp, repository, filename, ctx)


@mcp.tool(name="extract_flow", description="Extracts the execution flow of a program, starting from its primary entry point, and returns it in a structured JSON format.")
async def extract_flow(repository: str, filename: str, ctx: Context) -> str:
    content = get_file_content(repository, filename)
    # classification_json = "COBOL" #await classify_file(content, filename, repository, ctx)
    
    # language = "Unknown"
    # try:
    #     classification_data = json.loads(classification_json)
    #     language = classification_data.get("language", "Unknown")
    # except (json.JSONDecodeError, TypeError):
    #     await ctx.warning(f"Could not parse classification JSON for {filename}. Using 'Unknown'.")
    return await get_file_flow(
        mcp=mcp,
        repository=repository,
        filename=filename,
        classification="COBOL",
        ctx=ctx,
    )


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



    



@mcp.tool("file_classification", description="Classifies file content by programming language or file type.")
async def file_classification(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Classifies a file based on its content and filename.
    Takes filename and content as input to avoid file system operations.
    Returns programming language or file type classification.
    """
    
    content = get_file_content(repository_name, filename)   
    classification = await classify_file(content=content, filename=filename, repository=repository_name, ctx=ctx)
    return classification

@mcp.tool("retrieve_file_content", description="Retrieves the content of a file from the repository.")
async def retrieve_file_content(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Retrieves file content from the repository.
    Handles various file encodings and provides detailed error information.
    Returns just the file content for use by other tools.
    """
    return get_file_content(repository_name, filename)


@mcp.tool("find_edges", description="identify all points of interaction with external or internal components.")
async def find_edges(repository: str, filename: str, ctx: Context) -> str:
    """
    all points of interaction with external or internal components
    """
    print(f"repository_name: {repository} filename: {filename}")
    try:
        # content = get_file_content(repository, filename)
        full_path = get_file_full_path(repository, filename)
        print(f"full_path: {full_path[0]}")
        content = get_file_content_full_path(full_path[0])
        await ctx.info(f"Extracting edges from {filename}...")
        response = await extract_edges(content=content, ctx=ctx)
        return response
    except Exception as e:
        print(f"Error finding edges: {e}")
        await ctx.error(f"Error finding edges: {e}")
        return f"Error: {e}"    


