from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware, wrap_model_call, ModelRequest
from langchain.tools import tool as lc_tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from .base_agent import BaseAgent, TEMPERATURE, MAX_MODEL_CALLS, MAX_TOOL_CALLS, DEFAULT_SYSTEM_PROMPT

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


ROUTER_SYSTEM_PROMPT = (
    "You are a retrieval router for a Python codebase. "
    "Based on the query, call the single most appropriate retrieval tool:\n"
    "- semantic_search_codebase: conceptual queries ('how does X work?', 'what is Y responsible for?')\n"
    "- lexical_search_codebase: exact name lookups ('find ClassName', 'where is func_name called?')\n"
    "- graph_search_codebase: relationship queries ('what calls X?', 'what does Y depend on?', 'trace the call chain')\n"
    "Return the retrieved content as-is without summarising."
)


class AgenticRAGAgent(BaseAgent):
    """
    Two-level agentic RAG:
      outer agent  — synthesises the final answer using a single router tool
      router agent — picks the right retriever (semantic / lexical / graph) per query
    """

    def __init__(
        self,
        retriever_tools: list,
        model_name: str = DEFAULT_OPENAI_MODEL,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        middleware: list = None,
        temperature: float = TEMPERATURE,
        max_model_calls: int = MAX_MODEL_CALLS,
        max_tool_calls: int = MAX_TOOL_CALLS,
    ):
        super().__init__(
            tools=[],
            system_prompt=system_prompt,
            middleware=middleware,
            temperature=temperature,
            max_model_calls=max_model_calls,
            max_tool_calls=max_tool_calls,
        )
        self.model_name = model_name
        self.retriever_tools = retriever_tools

    def _build_router_tool(self):
        router_agent = create_agent(
            tools=self.retriever_tools,
            model=ChatOpenAI(model=self.model_name, temperature=0),
            system_prompt=SystemMessage(content=ROUTER_SYSTEM_PROMPT),
            middleware=[
                ModelCallLimitMiddleware(run_limit=5),
                ToolCallLimitMiddleware(run_limit=len(self.retriever_tools))
            ],
        )

        # closure captures router — avoids instance-method binding issues with @tool
        @lc_tool("router")
        def router_tool(query: str) -> str:
            """Routes the query to the most appropriate retriever: semantic, lexical, or graph."""
            result = router_agent.invoke(
                {"messages": [HumanMessage(content=query)]})
            return str(result["messages"][-1].content)

        return router_tool

    def build(self):
        router_tool = self._build_router_tool()
        return create_agent(
            tools=[router_tool],
            model=ChatOpenAI(model=self.model_name,
                             temperature=self.temperature),
            system_prompt=SystemMessage(content=self.system_prompt),
            middleware=self.middleware,
        )

    def agent_run(self, agent, question: str) -> list:
        messages = []

        for chunk in agent.stream(
            {"messages": [HumanMessage(content=question)]},
            stream_mode=["values"],
            version="v2",
        ):
            messages = chunk["data"]["messages"]

        context_gathered = [
            msg.content for msg in messages if isinstance(msg, ToolMessage)]

        answer = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content:
                answer = msg.content
                break

        return [answer, context_gathered]
