from langchain.tools import tool
from my_claude.context.retrievers.semantic_chroma import retrieve
from my_claude.observability.logger import get_logger

logger = get_logger(__name__)

@tool
def search_codebase(query: str) -> list[dict]:
    """
    Searches the indexed codebase for relevant code snippets based on the query.

    Args:
        query (str): The query string to search for.

    Returns:
        list[dict]: A list of dictionaries containing the retrieved documents and their metadata.
    """
    logger.info(f"Searching codebase for query: '{query}'")
    chunks = retrieve(query, k=5)

    results = []
    for chunk in chunks:
        results.append(
            f"File: {chunk['source']} (lines {chunk['start_line']}-{chunk['end_line']})\n"
            f"Type: {chunk['type']} — {chunk['name']}\n"
            f"Code:\n{chunk['content']}\n"
        )
    logger.info(f"Retrieved {len(chunks)} documents for query: '{query}'")
    return "\n---\n".join(results)

