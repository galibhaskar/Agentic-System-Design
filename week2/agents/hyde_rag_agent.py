from langchain.agents import create_agent
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware, wrap_model_call, ModelRequest
from langchain.tools import tool as lc_tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from .base_agent import BaseAgent, TEMPERATURE, MAX_MODEL_CALLS, MAX_TOOL_CALLS, DEFAULT_SYSTEM_PROMPT

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"


HYDE_SYSTEM_PROMPT = (
    "You generate a single hypothetical code snippet or document for retrieval.\n"
    "Write a compact, plausible-looking passage (4-7 sentences or a short code snippet) "
    "that could answer the question about a Python codebase.\n"
    "Do not add bullet points, no disclaimers, and no markdown."
)

class HyDERAGAgent(BaseAgent):
    """
    Hypothetical Document Embedding(HyDE) paraphrases the user query for better retrieval, then uses a router agent to pick the best retriever (semantic / lexical / graph) per query, before synthesising the final answer.

    core idea:
    - Don't embed the raw user query.
    - generate plausible hypothetical document(s).
    - Embed the hypothetical docs and fetch the nearest neighbors from the vector store.
    - This can help bridge the gap between the user's language and the language used in the agent.
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
        self.hyde_agent = create_agent(
            tools=[],
            model=ChatOpenAI(model=self.model_name, temperature=0),
            system_prompt=SystemMessage(content=HYDE_SYSTEM_PROMPT),
            middleware=[
                ModelCallLimitMiddleware(run_limit=5),
                ToolCallLimitMiddleware(run_limit=3)
            ],
        )

    def hyde_generator(self, query: str) -> str:
        """Generates hypothetical documents for the given query, then routes to the appropriate retriever."""
        result = self.hyde_agent.invoke(
            {"messages": [HumanMessage(content=query)]})

        hypothetical_document = result["messages"][-1].content

        print(
            f"HyDE generated hypothetical document:\n{hypothetical_document}\n")

        return hypothetical_document

    def build(self):
        return create_agent(
            tools= self.retriever_tools,
            model=ChatOpenAI(model=self.model_name,
                             temperature=self.temperature),
            system_prompt=SystemMessage(content=self.system_prompt),
            middleware=self.middleware,
        )

    def agent_run(self, agent, question: str) -> list:
        messages = []

        hypothetical_document = self.hyde_generator(question)

        for chunk in agent.stream(
            {"messages": [HumanMessage(content=hypothetical_document)]},
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
