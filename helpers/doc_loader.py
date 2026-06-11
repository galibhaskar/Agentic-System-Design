from pathlib import Path
from langchain_core.documents import Document

def load_all_docs(repo_path, file_extension=".py") -> list:
    """Loads all documents with the specified file extension from the given repository path."""

    docs = []

    print(f"Loading {file_extension} files from {repo_path}...")

    for path in Path(repo_path).rglob(f"*{file_extension}"):
        if path.is_file():
            # Ensure we can read the file
            content = path.read_text(encoding="utf-8", errors="ignore")

            docs.append(Document(page_content=content,
                        metadata={"source": str(path)}))

    return docs