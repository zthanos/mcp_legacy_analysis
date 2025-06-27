import subprocess
from pathlib import Path
from graph.graph_upsert import upsert_repository

WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

def extract_alias_from_url(repo_url: str) -> str:
    return Path(repo_url.rstrip("/").split("/")[-1]).stem

async def execute_fetch_repository(session, ctx, repo_url):
    print(f"repo_url: {repo_url}")

    repository_name = extract_alias_from_url(repo_url)
    repo_path = WORKSPACE / repository_name    
    if repo_path.exists():
        await ctx.info(f"Repository {repository_name} already exists locally")
    else:
        await ctx.info(f"Cloning repository {repository_name}...")
        subprocess.run(["git", "clone", repo_url, str(repo_path)], check=True)
        
    upsert_repository(session, repository_name)
    return repository_name

    