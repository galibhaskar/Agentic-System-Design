from .chroma import index_codebase as index_codebase_chroma, show_index as show_index_chroma
from .qdrant import index_codebase as index_codebase_qdrant, show_index as show_index_qdrant
from my_claude.observability.logger import get_logger
from my_claude.config import config

logger = get_logger(__name__)


def get_indexer():
    """
        fetches the indexer based on the config file
    """
    provider = config["rag"]["provider"]
    if provider == "chroma_db":
        return index_codebase_chroma
    elif provider == "qdrant":
        return index_codebase_qdrant
    else:
        logger.error(f"Invalid indexer type: {provider}")
        raise ValueError(f"Invalid indexer type: {provider}")


def show_semantic_index():
    """
        shows the semantic index based on the config file
    """
    provider = config["rag"]["provider"]
    if provider == "chroma_db":
        return show_index_chroma
    elif provider == "qdrant":
        return show_index_qdrant
    else:
        logger.error(f"Invalid indexer type: {provider}")
        raise ValueError(f"Invalid indexer type: {provider}")
