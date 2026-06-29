from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware
from langchain_core.messages import SystemMessage, HumanMessage

from my_claude.config import config
from my_claude.observability import get_logger
from my_claude.agent.tools import search_codebase
from my_claude.llm.factory import get_llm
from my_claude.memory.short_term import get_checkpointer, get_summarization_middleware

logger = get_logger(__name__)


def build_agent():
    """
        creates and return langchain agent
    """

    llm = get_llm()
    logger.info(f"Creating agent")
    checkpointer = get_checkpointer()

    SYSTEM_PROMPT = """You are a senior software engineer with deep knowledge of the codebase.
                    Always use the search_codebase tool before answering any question.
                    Reference specific file names, function names and line numbers in your answers.
                    If you cannot find the answer in the codebase, say so explicitly."""

    return create_agent(model=llm,
                        tools=[search_codebase],
                        system_prompt=SystemMessage(content=SYSTEM_PROMPT),
                        checkpointer=checkpointer,
                        middleware=[
                            ToolCallLimitMiddleware(
                                run_limit=config["agent"]["max_tool_calls"]),
                            ModelCallLimitMiddleware(
                                run_limit=config["agent"]["max_model_calls"]),
                            get_summarization_middleware()
                        ])
