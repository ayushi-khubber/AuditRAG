import json
import os
from pathlib import Path


def load_controls(path: str) -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_policy_documents(folder: str) -> list[dict]:
    """Return a list of {"source": filename, "text": file content} for every
    .txt file in the given folder."""
    docs = []
    folder_path = Path(folder)
    for file_path in sorted(folder_path.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8")
        docs.append({"source": file_path.name, "text": text})
    if not docs:
        raise FileNotFoundError(
            f"No .txt policy files found in {os.path.abspath(folder)}"
        )
    return docs
