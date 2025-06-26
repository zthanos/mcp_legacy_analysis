import re
import json
from graph_db import insert_repository
from pathlib import Path
from analysis import classify_file

WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)

def extract_alias_from_url(repo_url: str) -> str:
    return Path(repo_url.rstrip("/").split("/")[-1]).stem

async def execute_classify_repository(session, ctx, repository_name, repo_path):

    await ctx.info(f"Starting file classification for repository {repository_name}...")
    for file_path in repo_path.rglob("*"):
        if file_path.is_file():

            if ".git" in file_path.parts:
                continue
            if file_path.suffix == ".md":
                print(f"Skipping markdown file: {file_path}")
                insert_repository(session=session, 
                repository_name=repository_name, 
                full_path=str(file_path), 
                filename=str(file_path.name), 
                language="Text", 
                classification="Markdown")
                continue
            if file_path.suffix == ".ans":
                print(f"Skipping ansi file: {file_path}")
                insert_repository(session=session,
                repository_name=repository_name,
                full_path=str(file_path),
                filename=str(file_path.name),
                language=file_path.suffix.lower(),
                classification="ANSI")
                continue                
            image_suffixes = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".ico", ".webp"]
            if file_path.suffix.lower() in image_suffixes:
                print(f"Skipping image file: {file_path}")
                insert_repository(session=session,
                repository_name=repository_name,
                full_path=str(file_path),
                filename=str(file_path.name),
                language=file_path.suffix.lower(),
                classification="image")
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
                    classification_json = await classify_file(content, str(file_path.name), repository_name, ctx)
                    matches = re.findall(r"```json\s*(\{.*?\})\s*```", classification_json, re.DOTALL)
                    extracted_json = matches[0]
                    json_data = json.loads(extracted_json)
                    language = json_data.get("language", "Unknown")
                    classification = json_data.get("classification", "Unknown")
                    print(f"language: {language} classification: {classification} encoding_used: {encoding_used}")
                    insert_repository(session=session,
                    repository_name=repository_name,
                    full_path=str(file_path),
                    filename=str(file_path.name),
                    language=language,
                    classification=classification)
            except Exception as e:
                print(f"Error classifying file {file_path}: {e}")
                
    return repository_name    