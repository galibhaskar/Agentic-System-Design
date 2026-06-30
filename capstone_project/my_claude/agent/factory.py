from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware
from langchain_core.messages import SystemMessage, HumanMessage

from my_claude.config import config
from my_claude.observability import get_logger
from my_claude.agent.tools.retrieval_tools import search_codebase
from my_claude.agent.tools.terminal_tools import run_command_in_directory, run_command
from my_claude.llm.factory import get_llm
from my_claude.memory.short_term import get_summarization_middleware
from my_claude.agent.mcp.mcp_client import get_mcp_tools

logger = get_logger(__name__)


async def build_agent(checkpointer):
    """
        creates and return langchain agent
    """

    llm = get_llm()
    logger.info(f"Creating agent")
    mcp_tools = await get_mcp_tools()

    SYSTEM_PROMPT = """You are a senior software engineer with deep knowledge of the codebase.
                    Always use the search_codebase tool before answering any question.
                    Reference specific file names, function names and line numbers in your answers.
                    If you cannot find the answer in the codebase, say so explicitly."""

    return create_agent(model=llm,
                        tools=[
                            search_codebase,
                            run_command_in_directory,
                            run_command,
                            *mcp_tools
                        ],
                        system_prompt=SystemMessage(content=SYSTEM_PROMPT),
                        checkpointer=checkpointer,
                        middleware=[
                            ToolCallLimitMiddleware(
                                run_limit=config["agent"]["max_tool_calls"]),
                            ModelCallLimitMiddleware(
                                run_limit=config["agent"]["max_model_calls"]),
                            get_summarization_middleware()
                        ])
