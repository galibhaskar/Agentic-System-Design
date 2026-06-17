from abc import ABC, abstractmethod
from langchain_core.documents import Document

CHUNK_SIZE = 256
CHUNK_OVERLAP = 32
LANGUAGE = "python"


class BaseChunker(ABC):
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP, language: str = LANGUAGE):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.language = language

    @abstractmethod
    def chunk(self, docs: list[Document]) -> list[Document]:
        ...
