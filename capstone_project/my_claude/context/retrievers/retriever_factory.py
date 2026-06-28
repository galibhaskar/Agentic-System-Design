from my_claude.config import config
from my_claude.observability.logger import get_logger

logger = get_logger(__name__)

def get_retriever():
    """
        fetches the retriever based on the config file
    """
    provider = config["rag"]["provider"]
    from rich.console import Console
    console = Console()
    if provider == "chroma_db":
        console.print(f"[dim]Using ChromaDB retriever...[/dim]")
        from .chroma import retrieve as retrieve_chroma
        return retrieve_chroma
    elif provider == "qdrant":
        console.print(f"[dim]Using Qdrant retriever...[/dim]")
        from .qdrant import retrieve as retrieve_qdrant
        return retrieve_qdrant
    else:
        logger.error(f"Invalid retriever type: {provider}")
        raise ValueError(f"Invalid retriever type: {provider}")