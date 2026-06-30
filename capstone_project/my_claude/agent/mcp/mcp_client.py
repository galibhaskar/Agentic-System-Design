from langchain_mcp_adapters.client import MultiServerMCPClient

from my_claude.config import config
from my_claude.observability.logger import get_logger
from my_claude.mcp_config import load_mcp_config

logger = get_logger(__name__)

_mcp_tools = None


async def get_mcp_tools() -> list:
    """
    Retrieves a list of tools from the MCP server.

    Returns:
        list: A list of tools available on the MCP server.
    """

    global _mcp_tools

    if _mcp_tools is not None:
        return _mcp_tools

    mcp_config = load_mcp_config()

    if not mcp_config:
        logger.error(
            "Failed to load MCP configuration. Returning empty tool list.")
        return []

    logger.info(f"Connecting to MCP servers: {list(mcp_config.keys())}")

    client = MultiServerMCPClient(mcp_config)
    all_tools = await client.get_tools()
    _mcp_tools = _filter_selected_tools(all_tools)

    logger.info(f"Retrieved {len(_mcp_tools)} tools from MCP servers.")

    return _mcp_tools


def _filter_selected_tools(tools: list) -> list:
    """
    Filters the tools based on the selected tools in the configuration.

    Args:
        tools (list): List of tools retrieved from the MCP server.

    Returns:
        list: Filtered list of tools based on the configuration.
    """
    selected_tool_names = {
        tool_name
        for server_cfg in config.get("mcp", {}).values()
        for tool_name in server_cfg.get("selected_tools", [])
    }

    if not selected_tool_names:
        logger.warning(
            "No tools selected in MCP configuration. Returning all available tools.")
        return tools

    logger.info(f"Selected tool names: {selected_tool_names}")

    filtered_tools = [
        tool for tool in tools if tool.name in selected_tool_names]

    if not filtered_tools:
        logger.warning(
            "No matching tools found based on the configuration. Returning all available tools.")
        return tools

    return filtered_tools
