from abc import ABC, abstractmethod
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

TEMPERATURE = 0
MAX_MODEL_CALLS = 10
MAX_TOOL_CALLS = 2
DEFAULT_SYSTEM_PROMPT = (
            "You are a senior engineer. Always use your available retrieval tool before answering. "
            "When calling the retrieval tool, output only the structured tool arguments. Do not wrap the tool call in raw HTML tags, backticks, or XML formatting."
            "Reference specific file and function names. "
            "If not found say 'I could not find that in the codebase'.")


class BaseAgent(ABC):
    def __init__(
        self,
        tools: list = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        middleware: list = None,
        temperature: float = TEMPERATURE,
        max_model_calls: int = MAX_MODEL_CALLS,
        max_tool_calls: int = MAX_TOOL_CALLS,
    ):
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.middleware = middleware if middleware is not None else [
            ModelCallLimitMiddleware(run_limit=max_model_calls),
            ToolCallLimitMiddleware(run_limit=max_tool_calls),
        ]

    @abstractmethod
    def build(self):
        ...

    @abstractmethod
    def agent_run(self, agent, question: str) -> list:
        ...
