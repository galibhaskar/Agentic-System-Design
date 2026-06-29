import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from pathlib import Path
from langchain.agents.middleware import SummarizationMiddleware

from my_claude.config import config
from my_claude.observability.logger import get_logger
from my_claude.llm.factory import get_llm

logger = get_logger(__name__)


def get_checkpointer() -> SqliteSaver:
    dbpath = config["memory"]["persist_directory"]
    Path(dbpath).parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Using SQLite database at: {dbpath}")
    conn = sqlite3.connect(dbpath, check_same_thread=False)
    return SqliteSaver(conn)


def get_session_history(thread_id: str) -> list[dict]:
    """
    Returns the history for a specific session.
    """
    checkpointer = get_checkpointer()
    config = {
        "configurable": {"thread_id": thread_id}
    }

    checkpoint = checkpointer.get(config)

    if not checkpoint:
        logger.info(f"No existing session found for thread_id: {thread_id}")
        return []

    logger.info(f"Retrieved session history for thread_id: {thread_id}")
    messages = checkpoint["channel_values"].get("messages", [])

    return messages


def get_summarization_middleware() -> SummarizationMiddleware:
    """
    Returns a summarization middleware instance.
    """
    return SummarizationMiddleware(
        model=get_llm(),
        trigger=("tokens", config["memory"]["summarize_threshold"]),
        keep=("messages", config["memory"]["keep_last_messages"]),
    )