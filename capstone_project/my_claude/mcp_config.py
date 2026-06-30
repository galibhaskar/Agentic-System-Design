import os
import re
import json
from pathlib import Path

from my_claude.config import config
from my_claude.observability.logger import get_logger

logger = get_logger(__name__)

_CONFIG_PATH = Path(__file__).parent / "mcp_servers.json"


def load_mcp_config() -> dict:
    """
    Loads the MCP server configuration from a JSON file and resolves any environment variables.

    Returns:
        dict: The MCP server configuration.
    """
    if not _CONFIG_PATH.exists():
        logger.error(f"Configuration file {_CONFIG_PATH} does not exist.")
        return {}

    with open(_CONFIG_PATH, "r") as f:
        config_data = json.load(f)

    return resolve_env_in_dict(config_data.get("mcp_servers", {}))


def resolve_env_in_dict(data) -> dict:
    if isinstance(data, str):
        return _resolve_env(data)
    elif isinstance(data, dict):
        return {key: resolve_env_in_dict(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [resolve_env_in_dict(item) for item in data]


def _resolve_env(value: str) -> str:
    return re.sub(r"\$\{(\w+)\}", lambda m: os.getenv(m.group(1), ""), value)
