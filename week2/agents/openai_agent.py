from langchain.agents import create_agent
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_openai import ChatOpenAI
from .base_agent import BaseAgent, TEMPERATURE, MAX_MODEL_CALLS, MAX_TOOL_CALLS, DEFAULT_SYSTEM_PROMPT

DEFAULT_OPENAI_MODEL = "gpt-4o"


class OpenAIAgent(BaseAgent):
    def __init__(
        self,
        model_name: str = DEFAULT_OPENAI_MODEL,
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
            model=ChatOpenAI(model=self.model_name, temperature=self.temperature),
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

        context_gathered = [msg.content for msg in messages if isinstance(msg, ToolMessage)]

        answer = next(
            (msg.content for msg in reversed(messages) if isinstance(msg, AIMessage) and msg.content),
            "",
        )

        return [answer, context_gathered]
