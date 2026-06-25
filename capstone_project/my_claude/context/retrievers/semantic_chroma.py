import chromadb
from my_claude.config import config
from my_claude.llm.factory import get_embedder
from my_claude.observability.logger import get_logger

logger = get_logger(__name__)

def retrieve(query: str, k:int = 5) -> list[dict]:
    """
    Retrieve the top-k most relevant documents from the ChromaDB collection based on the query.

    Args:
        query (str): The query string to search for.
        k (int): The number of top documents to retrieve.

    Returns:
        list[dict]: A list of dictionaries containing the retrieved documents and their metadata.
    """
    client = chromadb.PersistentClient(path=config["chroma_db"]["persist_directory"])
    collection = client.get_or_create_collection(name=config["chroma_db"]["collection_name"])

    logger.info(f"Retrieving top {k} documents for query: '{query}' from collection '{config['chroma_db']['collection_name']}'")

    embedder = get_embedder()
    query_embedding = embedder.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=k,
        include=["documents", "metadatas", "distances"]
    )

    retrieved_docs = []
    
    for doc, metadata, distance in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        retrieved_docs.append({
            "content": doc,
            "source": metadata["source"],
            "name": metadata["name"],
            "type": metadata["type"],
            "start_line": metadata["start_line"],
            "end_line": metadata["end_line"],
            "distance": distance
        })

    logger.info(f"Retrieved {len(retrieved_docs)} documents for query: '{query}'")
    return retrieved_docs