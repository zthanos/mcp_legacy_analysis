import re
import json
from pathlib import Path
from graph.graph_upsert import upsert_document
from tools.document import document_analysis
from sampling import sample_helper

WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)


def extract_alias_from_url(repo_url: str) -> str:
    return Path(repo_url.rstrip("/").split("/")[-1]).stem


async def execute_classify_repository(session, ctx, repository_name):
    repo_path = WORKSPACE / repository_name
    await ctx.info(f"Starting file classification for repository {repository_name}...")

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file() or ".git" in file_path.parts:
            continue

        file_type, language, classification = classify_by_extension(file_path)

        if file_type == "skip":
            await register_document(
                session, repository_name, file_path, language, classification, ""
            )
            continue

        print(f"Processing file: {file_path}")

        content, encoding_used = safe_read_file(file_path)
        if not content:
            print(f"Skipping unreadable file: {file_path}")
            continue

        try:
            print(f"Document Analysis: {file_path.name}")

            analysis_data = await document_analysis(
                session=session,
                repository_name=repository_name,
                filename=file_path.name,
                ctx=ctx
            )
            print(analysis_data)

            await register_document(
                session,
                repository_name,
                file_path,
                language,
                classification,
                analysis_data,
            )

        except Exception as e:
            print(f"Error classifying file {file_path}: {e}")

    return repository_name


# ----------------- Helper Functions -----------------


def classify_by_extension(file_path):
    ext = file_path.suffix.lower()
    image_ext = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".ico", ".webp"]

    if ext == ".md":
        return "skip", "Text", "Markdown"
    if ext == ".ans":
        return "skip", ext, "ANSI"
    if ext in image_ext:
        return "skip", ext, "Image"

    return "process", None, None


def safe_read_file(file_path):
    for encoding in ["utf-8", "cp1252", "iso-8859-1", "cp037"]:
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                return f.read(), encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None, None


async def register_document(
    session, repository_name, file_path, language, classification, analysis_data
):
    upsert_document(
        session=session,
        repository_name=repository_name,
        full_path=str(file_path),
        filename=str(file_path.name),
        language=language,
        classification=classification,
        analysis=analysis_data,
    )
    print(f"Registered {file_path} as {classification}")
