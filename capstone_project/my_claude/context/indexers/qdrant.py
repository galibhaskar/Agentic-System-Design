import os
from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from langchain_core.documents import Document
from qdrant_client import QdrantClient

from my_claude.config import config
from my_claude.observability.logger import get_logger
from my_claude.llm.factory import get_embedder
from my_claude.context.indexers.code_parser import parse_file, get_source_files

logger = get_logger(__name__)

RETRIEVAL_MODE_MAPPING = {
    "hybrid": RetrievalMode.HYBRID,
    "sparse": RetrievalMode.SPARSE,
    "dense": RetrievalMode.DENSE,
}

def _get_retrieval_mode() -> RetrievalMode:
    retrieval_mode_str = config["qdrant"]["retrieval_mode"].lower()

    return RETRIEVAL_MODE_MAPPING[retrieval_mode_str]

def index_codebase(repo_path: str) -> QdrantVectorStore:
    """
    Indexes the codebase located at the given path using Qdrant.
    """
    logger.info(f"Indexing codebase at {repo_path}")

    embedder = get_embedder()
    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    collection_name = config["qdrant"]["collection_name"]
    retrieval_mode = _get_retrieval_mode()

    from rich.console import Console
    console = Console()
    console.print(f"[dim]Using retrieval mode: {retrieval_mode.name}[/dim]")
    logger.info(f"Using retrieval mode: {retrieval_mode.name}")

    qdrant_client = QdrantClient(url=url, api_key=api_key)

    exisiting = [
        coll.name for coll in qdrant_client.get_collections().collections]

    if collection_name in exisiting:
        info = qdrant_client.get_collection(collection_name)
        if info.points_count > 0:
            logger.info(
                f"Collection '{collection_name}' already exists with {info.points_count} points")
            return QdrantVectorStore.from_existing_collection(
                url=url,
                api_key=api_key,
                collection_name=collection_name,
                embedding=embedder,
                sparse_embedding=FastEmbedSparse(model_name="Qdrant/bm25"),
                retrieval_mode=retrieval_mode
            )
    logger.info(f"Starting indexing for collection '{collection_name}'")
    files = get_source_files(repo_path)

    docs = []

    for filepath in files:
        try:
            chunks = parse_file(filepath)
        except (SyntaxError, ValueError) as e:
            logger.error(f"Skipping {filepath}: {e}")
            continue

        for chunk in chunks:
            docs.append(Document(
                page_content=chunk.content,
                metadata={
                    "source": chunk.source,
                    "name": chunk.name,
                    "type": chunk.type,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                }
            ))
            logger.debug(
                f"  Indexed {chunk.type} '{chunk.name}' from {filepath}")

    vector_store = QdrantVectorStore.from_documents(
        documents=docs,
        api_key=api_key,
        url=url,
        collection_name=collection_name,
        embedding=embedder,
        sparse_embedding=FastEmbedSparse(model_name="Qdrant/bm25"),
        retrieval_mode=retrieval_mode,
        batch_size=config["qdrant"]["batch_size"]
    )

    logger.info(
        f"Indexing complete for collection '{collection_name}' with {len(docs)} documents")
    return vector_store


def show_index(vector_store: QdrantVectorStore) -> None:
    """Display the number of documents stored in the Qdrant collection."""
    from rich.console import Console
    console = Console()

    collection_name = config["qdrant"]["collection_name"]
    qdrant_client = vector_store.client
    info = qdrant_client.get_collection(collection_name)

    logger.info(
        f"\nQdrant Collection '{collection_name}' — {info.points_count} documents\n")

    results = qdrant_client.scroll(
        collection_name=collection_name,
        with_payload=True,
        with_vectors=False,
        limit=1000)

    points = results[0]

    console.print(f"\n[bold]Hybrid Index — {len(points)} chunks[/bold]\n")

    for i, point in enumerate(points):
        content = point.payload.get("page_content", "")
        meta = point.payload.get("metadata", {})
        console.print(
            f"[bold cyan]── Chunk {i+1} ──────────────────────────[/bold cyan]")
        console.print(f"  File     : {meta.get('source', 'unknown')}")
        console.print(
            f"  Name     : {meta.get('name', 'unknown')} ({meta.get('type', 'unknown')})")
        console.print(
            f"  Lines    : {meta.get('start_line')} - {meta.get('end_line')}")
        console.print(f"  Code     :\n[dim]{content[:300]}[/dim]\n")
