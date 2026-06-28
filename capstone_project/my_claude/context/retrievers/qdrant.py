from langchain_qdrant import QdrantVectorStore, RetrievalMode, FastEmbedSparse
from my_claude.config import config
from my_claude.observability.logger import get_logger
from my_claude.llm.factory import get_embedder
import os

logger = get_logger(__name__)

ReTRIEVAL_MODE_MAPPING = {
    "hybrid": RetrievalMode.HYBRID, 
    "sparse": RetrievalMode.SPARSE,
    "dense": RetrievalMode.DENSE,
}

def _get_retrieval_mode() -> RetrievalMode:
    """
    Get the retrieval mode from the configuration.

    Returns:
        RetrievalMode: The retrieval mode to be used for Qdrant.
    """
    retrieval_mode_str = config["qdrant"]["retrieval_mode"].lower()
    return ReTRIEVAL_MODE_MAPPING[retrieval_mode_str]

def retrieve(query: str, k: int = 5) -> list:
    """
    Retrieve relevant documents based on the query.

    Args:
        query (str): The query string to search for.
        k (int): The number of top results to retrieve.

    Returns:
        list: A list of retrieved documents.
    """
    embedder = get_embedder()
    collection_name = config["qdrant"]["collection_name"]

    url = os.getenv("QDRANT_URL")
    api_key = os.getenv("QDRANT_API_KEY")
    retrieval_mode = _get_retrieval_mode()

    from rich.console import Console
    console = Console()
    console.print(f"[dim]Using retrieval mode: {retrieval_mode.name}[/dim]")

    vector_store = QdrantVectorStore.from_existing_collection(
        url=url,
        api_key=api_key,
        embedding=embedder,
        collection_name=collection_name,
        sparse_embedding=FastEmbedSparse(model_name="Qdrant/bm25"),
        retrieval_mode=retrieval_mode
    )

    logger.info(f"Retrieving top {k} documents for query: '{query}'")

    results = vector_store.similarity_search_with_score(query, k=k)

    chunks = []

    for doc, score in results:
        chunks.append({
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Unknown"),
            "name": doc.metadata.get("name", "Unknown"),
            "type": doc.metadata.get("type", "Unknown"),
            "start_line": doc.metadata.get("start_line", -1),
            "end_line": doc.metadata.get("end_line", -1),
            "distance": score
        })

        logger.debug(f"  Retrieved {doc.metadata.get('type', 'Unknown')} '{doc.metadata.get('name', 'Unknown')}' from {doc.metadata.get('source', 'Unknown')} (distance: {score:.4f})")
    
    logger.info(f"Retrieved {len(chunks)} documents for query: '{query}'")

    return chunks
