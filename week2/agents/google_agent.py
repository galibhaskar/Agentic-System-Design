from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from .base_agent import BaseAgent, TEMPERATURE, MAX_MODEL_CALLS, MAX_TOOL_CALLS, DEFAULT_SYSTEM_PROMPT

DEFAULT_GOOGLE_MODEL = "gemini-2.0-flash"


class GoogleAgent(BaseAgent):
    def __init__(
        self,
        model_name: str = DEFAULT_GOOGLE_MODEL,
        tools: list = None,
        system_prompt: str = DEFAULT_SYSTEM_PROMPT,
        middleware: list = None,
        temperature: float = TEMPERATURE,
        max_model_calls: int = MAX_MODEL_CALLS,
        max_tool_calls: int = MAX_TOOL_CALLS,
    ):
        super().__init__(
            tools=tools,
            system_prompt=system_prompt,
            middleware=middleware,
            temperature=temperature,
            max_model_calls=max_model_calls,
            max_tool_calls=max_tool_calls,
        )
        self.model_name = model_name

    def build(self):
        return create_agent(
            tools=self.tools,
            model=ChatGoogleGenerativeAI(model=self.model_name, temperature=self.temperature),
            system_prompt=SystemMessage(content=self.system_prompt),
            middleware=self.middleware,
        )

    def agent_run(self, agent, question: str) -> list:
        # Gemini returns candidates; content may be nested under .text for some response types
        response = agent.invoke({"messages": [HumanMessage(content=question)]})
        messages = response.get("messages", [])

        context_gathered = [msg.content for msg in messages if isinstance(msg, ToolMessage)]

        answer = next(
            (msg.content for msg in reversed(messages) if isinstance(msg, AIMessage) and msg.content),
            "",
        )

        return [answer, context_gathered]
