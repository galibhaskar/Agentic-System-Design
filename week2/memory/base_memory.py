from abc import ABC, abstractmethod

class BaseMemory(ABC):
    def __init__(self):
        self.threads_info = []
        self.current_thread = None
        self.conversation_history = []
        self.llm = None  # Placeholder for the LLM instance

    @abstractmethod
    def save_message(self, thread_name, role, message):
        ...
    
    @abstractmethod
    def list_threads(self):
        ...

    @abstractmethod
    def add_thread(self, thread_name):
        ...
    
    @abstractmethod
    def switch_thread(self, thread_name):
        ...
        
    @abstractmethod
    def load_conversation_history(self):
        ...
    
    def display_conversation_history(self):
        if self.current_thread is None:
            raise ValueError("No current thread selected.")

        for message in self.current_thread['messages']:
            print(f"{message.role}: {message.content}")

    def ask(self, question):
        if self.current_thread is None:
            raise ValueError("No current thread selected.")

        if self.llm is None:
            raise ValueError("LLM instance is not set.")

        # For demonstration purposes, we will just echo the question back.
        self.save_message(self.current_thread['name'], 'user', question)

        response = self.llm.invoke(self.current_thread['messages']).content

        self.save_message(self.current_thread['name'], 'assistant', response)

        return response