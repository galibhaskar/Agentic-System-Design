from abc import ABC, abstractmethod
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools.retriever import create_retriever_tool

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
TOP_K = 4
SIMILARITY_THRESHOLD = 0.7


class BaseVectorStore(ABC):
    tool_name: str = "search_codebase"
    tool_description: str = "Search the codebase for relevant code snippets."

    def __init__(self, embedding_model: str = EMBEDDING_MODEL, top_k: int = TOP_K):
        self.embedding_model = embedding_model
        self.top_k = top_k

    @abstractmethod
    def build(self, chunks: list[Document]) -> None:
        ...

    @abstractmethod
    def as_retriever(self, k: int = TOP_K) -> BaseRetriever:
        ...

    def as_retriever_tool(self, name: str = None, description: str = None, k: int = TOP_K):
        return create_retriever_tool(
            self.as_retriever(k=k),
            name=name or self.tool_name,
            description=description or self.tool_description,
        )
