from .base_memory import BaseMemory
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

class STMInMemory(BaseMemory):
    def __init__(self):
        super().__init__()
        self.threads_info = [
            {
                "name": "default_thread",
                "messages": [
                    SystemMessage(
                        content="You are a helpful assistant. You will answer questions based on the context provided. If you don't know the answer, say 'I don't know.'"),
                ]
            }
        ]
        self.switch_thread("default_thread")
        self.load_conversation_history()
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    def save_message(self, thread_name, role, content):
        if thread_name not in [thread['name'] for thread in self.threads_info]:
            raise ValueError(f"Thread '{thread_name}' does not exist.")

        if role == 'assistant':
            message = AIMessage(content=content)
        elif role == 'user':
            message = HumanMessage(content=content)
        elif role == 'system':
            message = SystemMessage(content=content)
        else:
            message = ToolMessage(content=content)

        for thread in self.threads_info:
            if thread['name'] == thread_name:
                thread['messages'].append(message)
                break

        self.conversation_history = self.load_conversation_history()

    def list_threads(self):
        return [thread['name'] for thread in self.threads_info]

    def add_thread(self, thread_name):
        if thread_name in [thread['name'] for thread in self.threads_info]:
            raise ValueError(f"Thread '{thread_name}' already exists.")

        self.threads_info.append({'name': thread_name, 'messages': []})

    def switch_thread(self, thread_name):
        if thread_name not in [thread['name'] for thread in self.threads_info]:
            raise ValueError(f"Thread '{thread_name}' does not exist.")

        self.current_thread = next(
            thread for thread in self.threads_info if thread['name'] == thread_name)

    def load_conversation_history(self):
        if self.current_thread is None:
            raise ValueError("No current thread selected.")

        self.conversation_history = self.current_thread['messages']
