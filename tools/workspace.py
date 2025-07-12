from fastmcp.resources import  TextResource, resource_manager
from pathlib import Path

WORKSPACE = Path("./workspace")

def execute_expose_workspace(ctx):
    results = []
    repo_path = WORKSPACE
    for file_path in repo_path.rglob("*"):
        if file_path.is_file():
            results.append(file_path)
    return results
    


