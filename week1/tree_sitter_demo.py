import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tree_sitter_language_pack import ProcessConfig, process
from helpers import doc_loader
from langchain_core.documents import Document
from pathlib import Path

config = ProcessConfig(
    language="python",
    structure=True,
    docstrings=True,
    chunk_max_size=1000,
)

def build_chunks(docs: list[Document]) -> list:
    chunks = []
    
    # Process the source code using the tree-sitter language pack
    for doc in docs:
        source_code = doc.page_content
        result = process(source_code, config)

        for chunk in result.chunks:
            chunks.append(Document(
                page_content=chunk.content,
                metadata={
                    "language": "python",
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "chunk_index": chunk.metadata.chunk_index,
                    "size_bytes": chunk.end_byte - chunk.start_byte,
                }
            ))

    return chunks

if __name__ == "__main__":
    docs = doc_loader.load_all_docs(repo_path=Path(
        __file__).resolve().parent / "datasources", file_extension=".py")
    print(f"Loaded {len(docs)} documents.")

    chunks = build_chunks(docs)

    for i, chunk in enumerate(chunks):
        print(f"Chunk {i}:")
        print(f"Metadata: {chunk.metadata}")
        print()