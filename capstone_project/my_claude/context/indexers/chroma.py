import chromadb
from my_claude.config import config
from my_claude.observability.logger import get_logger
from my_claude.context.indexers.code_parser import parse_file, get_source_files
from my_claude.llm.factory import get_embedder
from rich.console import Console

logger = get_logger(__name__)
console = Console()

def index_codebase(repo_path: str) -> chromadb.Collection:
    """
    Indexes the codebase located at the given path using ChromaDB.

    Args:
        repo_path (str): Path to the codebase directory.
    """
    logger.info(f"Indexing codebase at: {repo_path}")

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=config["chroma_db"]["persist_directory"])

    # Create a collection for the codebase
    collection = client.get_or_create_collection(name=config["chroma_db"]["collection_name"])

    # Get source files from the codebase
    source_files = get_source_files(repo_path)

    embedder = get_embedder()

    for filepath in source_files:
        try:
            chunks = parse_file(filepath)
        except (SyntaxError, ValueError) as e:
            logger.error(f"Skipping {filepath}: {e}")
            continue

        for chunk in chunks:
            embedding = embedder.embed_query(chunk.content)

            # Unique ID for each chunk — source + name + line prevents duplicates on re-index
            doc_id = f"{chunk.source}::{chunk.name}::{chunk.start_line}"

            collection.upsert(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[chunk.content],
                metadatas=[{
                    "source": chunk.source,
                    "name": chunk.name,
                    "type": chunk.type,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                }]
            )
            logger.debug(f"  Indexed {chunk.type} '{chunk.name}' from {filepath}")

    logger.info(f"Semantic indexing complete. Total chunks: {collection.count()}")
    return collection


def show_index(collection: chromadb.Collection) -> None:
    """Display all documents stored in the ChromaDB collection."""
    results = collection.get(include=["documents", "metadatas", "embeddings"])
    console.print(f"\n[bold]Semantic Index — {collection.count()} chunks[/bold]\n")

    for i, (doc, meta, emb) in enumerate(zip(
        results["documents"],
        results["metadatas"],
        results["embeddings"]
    )):
        console.print(f"[bold cyan]── Chunk {i+1} ──────────────────────────[/bold cyan]")
        console.print(f"  File     : {meta['source']}")
        console.print(f"  Name     : {meta['name']} ({meta['type']})")
        console.print(f"  Lines    : {meta['start_line']} - {meta['end_line']}")
        console.print(f"  Embedding: [{', '.join(f'{v:.4f}' for v in emb[:5])}...] ({len(emb)} dims)")
        console.print(f"  Code     :\n[dim]{doc[:300]}[/dim]\n")
