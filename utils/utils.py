import re
import json
from pathlib import Path
import os

WORKSPACE = Path("./workspace")
WORKSPACE.mkdir(exist_ok=True)


def languages_from_json(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_json_from_text(text):
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
    if not matches:
        raise ValueError("No valid JSON found in LLM response")
    return json.loads(matches[0])


def safe_read_file(file_path):
    for encoding in ['utf-8', 'cp1252', 'iso-8859-1', 'cp037']:
        try:
            with open(file_path, "r", encoding=encoding, errors="replace") as f:
                return f.read(), encoding
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None, None


def classify_by_extension(file_path: Path):
    """
    Classifies a file by extension into skip/process and gives type info.

    Args:
        file_path (Path): Path object of the file.

    Returns:
        tuple: ("skip" or "process", language, classification)
    """
    ext = file_path.suffix.lower()
    image_ext = [".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".ico", ".webp"]

    if ext == ".md":
        return "skip", "Text", "Markdown"
    if ext == ".ans":
        return "skip", ext, "ANSI"
    if ext in image_ext:
        return "skip", ext, "Image"

    return "process", None, None


def get_file_content_full_path(full_path: str) -> str:
    with open(full_path, "r") as f:
        return f.read()


def get_file_content(repository_name: str, filename: str) -> str:
    """
    Retrieves file content from the repository by searching in the workspace.

    Args:
        repository_name (str): Repository alias.
        filename (str): Filename to search.

    Returns:
        str: File content or error message.
    """
    try:
        repo_path = WORKSPACE / repository_name

        # Handle both absolute and relative paths
        if os.path.isabs(filename):
            file_path = Path(filename)
        else:
            file_path = None
            for root, dirs, files in os.walk(repo_path):
                if filename in files:
                    file_path = Path(root) / filename
                    break

            if file_path is None:
                return f"ERROR: File '{filename}' not found in repository '{repository_name}'"

        if not file_path.exists():
            return f"ERROR: File not found: {file_path}"

        # Try to read with various encodings
        for encoding in ['utf-8', 'cp1252', 'iso-8859-1', 'cp037']:
            try:
                with open(file_path, "r", encoding=encoding, errors="replace") as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue

        # Last resort: binary mode
        with open(file_path, "rb") as f:
            raw_content = f.read()
            return raw_content.decode('utf-8', errors='replace')

    except Exception as e:
        return f"ERROR: Unable to retrieve file content: {str(e)}"
