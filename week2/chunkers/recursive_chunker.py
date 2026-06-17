from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .base_chunker import BaseChunker, CHUNK_SIZE, CHUNK_OVERLAP, LANGUAGE


class RecursiveChunker(BaseChunker):
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP, language: str = LANGUAGE):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap, language=language)

    def chunk(self, docs: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=self.language,
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )
        return splitter.split_documents(docs)
