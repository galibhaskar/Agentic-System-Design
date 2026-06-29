from my_claude.config import config
from my_claude.observability.logger import get_logger
from pathlib import Path
import uuid

logger = get_logger(__name__)

def _get_session_file_path() -> Path:
    """
    Returns the path to the session file.
    """
    return Path(config["memory"]["persist_directory"]).parent / "current_session"

def create_session() -> None:
    """
    Creates a new session for the user.
    """
    logger.info("Creating a new session.")
    session_id = str(uuid.uuid4())
    session_file = _get_session_file_path()

    session_file.parent.mkdir(parents=True, exist_ok=True)
    session_file.write_text(session_id)

    logger.info(f"Started new session with ID: {session_id}")

    return session_id

def get_current_session() -> str:
    """
    Retrieves the current session ID.
    """
    session_file = _get_session_file_path()
    if not session_file.exists():
        logger.warning("No active session found. Creating a new one.")
        return create_session()

    session_id = session_file.read_text().strip()
    logger.info(f"Retrieved current session ID: {session_id}")
    return session_id

def switch_session(new_session_id: str) -> str:
    """
    Switches to a different session.
    """
    logger.info(f"Switching to session ID: {new_session_id}")
    session_file = _get_session_file_path()
    session_file.write_text(new_session_id)
    return new_session_id