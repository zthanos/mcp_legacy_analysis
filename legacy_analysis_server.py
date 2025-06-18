from fastmcp import FastMCP, Context
from pathlib import Path
from analysis import get_file_content, classify_file
from data_structure import ExtractDataStructures
from flow_analysis import extract_flow
import subprocess
import os
import git
import re

import json



# Create MCP Server
mcp = FastMCP(name="Legacy Code Analysis Service")


WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

_repo_registry = {}  # Keeps track of aliases and paths

def extract_alias_from_url(repo_url: str) -> str:
    return Path(repo_url.rstrip("/").split("/")[-1]).stem


@mcp.tool(name="fetch_repository", description="Clones a COBOL repository and registers it as a resource.")
def fetch_repository(repo_url: str) -> str:
    alias = extract_alias_from_url(repo_url)
    repo_path = WORKSPACE / alias

    if not repo_path.exists():
        subprocess.run(["git", "clone", repo_url, str(repo_path)], check=True)

    # Register the alias as MCP resource
    @mcp.resource(f"resource://{alias}")
    def repo_root() -> str:
        return str(repo_path)

    # Also store it for later use if needed
    _repo_registry[alias] = str(repo_path)

    # ctx.log.info(f"Repository {alias} fetched and available at resource://{alias}")
    return alias

    
@mcp.tool(name="extract_data_structure", description="Extracts COBOL data structures from a file inside a registered resource.")
async def get_data_structure(repository: str, filename: str, ctx: Context) -> str:
    return ExtractDataStructures.cobol_data_structure(mcp, repository, filename, ctx)


@mcp.tool(name="extract_flow", description="Extracts the execution flow of a program, starting from its primary entry point, and returns it in a structured JSON format.")
async def extract_flow(repository: str, filename: str, ctx: Context) -> str:
    
    extract_flow(repository=repository, filename=filename, classification="flow", ctx=ctx)


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
    classification = await classify_file(content, filename, ctx)
    return classification

@mcp.tool("retrieve_file_content", description="Retrieves the content of a file from the repository.")
async def retrieve_file_content(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Retrieves file content from the repository.
    Handles various file encodings and provides detailed error information.
    Returns just the file content for use by other tools.
    """
    return retrieve_file_content(repository_name, filename)


@mcp.tool("retrieve_file_with_classification", description="Retrieves file content along with its classification.")
async def retrieve_file_with_classification(repository_name: str, filename: str, ctx: Context) -> str:
    """
    Retrieves file content and provides classification analysis.
    This is a convenience tool that combines file retrieval and classification.
    """
    try:
        # Get file content
    
        prompt = f"retrieve_file_content {repository_name} {filename}"
        messages = [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt
                }
            }
        ]
        
        content = await ctx.sample(
            messages=messages,
            temperature=0.0
        )        
        
        
        if content.startswith("ERROR:"):
            return content
        
        prompt = f"file_classification  {filename}\n {content.text().strip()}"
        messages = [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": prompt
                }
            }
        ]
        
        classification_result = await ctx.sample(
            messages=messages,
            temperature=0.0
        )        
        
        
        
        # Extract classification from result
        classification = classification_result if isinstance(classification_result, str) else str(classification_result)
        
        # Get file metadata
        repo_alias = repository_name.replace("resource://", "")
        repo_path = WORKSPACE / repo_alias
        
        # Find the actual file path for metadata
        file_path = None
        for root, dirs, files in os.walk(repo_path):
            if filename in files:
                file_path = Path(root) / filename
                break
        
        if file_path:
            file_size = len(content)
            relative_path = os.path.relpath(file_path, repo_path)
        else:
            file_size = len(content)
            relative_path = filename
        
        # Format the response
        result = f"File: {filename}\n"
        result += f"Path: {relative_path}\n"
        result += f"Size: {file_size} characters\n"
        result += f"Classification: {classification}\n"
        result += f"{'='*50}\n"
        result += f"Content:\n{content}"
        
        return result
        
    except Exception as e:
        return f"ERROR: {str(e)}"

    """
    Generates C4 architecture diagrams from analyzed system components.
    Creates both Level 1 (System Context) and Level 2 (Container) diagrams.
    """
    try:
        # Get all available resources
        all_resources = await ctx.list_resources()
        
        if not all_resources:
            return "No resources found for C4 model generation."
        
        # Filter for relevant analysis resources
        relevant_resources = []
        resource_content = {}
        
        for uri in all_resources:
            # Look for resources that contain system analysis data
            if any(keyword in uri.lower() for keyword in ['structure', 'methods', 'flow', 'analysis']):
                try:
                    content = await ctx.get_resource(uri)
                    relevant_resources.append(uri)
                    resource_content[uri] = content
                except Exception as e:
                    continue  # Skip resources that can't be read
        
        if not relevant_resources:
            return "No relevant analysis resources found for C4 model generation."
        
        # Prepare the analysis prompt
        resources_summary = []
        for uri, content in resource_content.items():
            resources_summary.append(f"Resource: {uri}\nContent: {str(content)[:2000]}...\n")
        
        analysis_prompt = f"""
You are a software architect analyzing a legacy system. Based on the provided system analysis data, generate C4 model diagrams.

## INSTRUCTIONS:

### Level 1 - System Context Diagram:
- Identify main actors (users, external systems)
- Show the system boundary
- Identify key external interactions
- Use Mermaid C4Context syntax

### Level 2 - Container Diagram:
- Break down the system into containers (applications, databases, services)
- Show technology stack for each container
- Identify data flows and relationships
- Include COBOL programs, Python services, CLIST scripts, databases, etc.
- Use Mermaid C4Container syntax

## INPUT DATA:
{chr(10).join(resources_summary)}

## OUTPUT FORMAT:
Provide two separate Mermaid diagrams:
1. C4 Context diagram (Level 1)
2. C4 Container diagram (Level 2)

Include brief descriptions for each component and relationship.
"""
        
        messages = [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": analysis_prompt
                }
            }
        ]
        
        response = await ctx.sample(
            messages=messages,
            system_prompt="You are an expert software architect specializing in legacy system modernization and C4 modeling. Focus on creating clear, accurate architectural diagrams.",
            temperature=0.3
        )
        
        return response.text.strip()
        
    except Exception as e:
        return f"Error generating C4 model: {str(e)}"