from langchain_core.documents import Document
from tree_sitter_language_pack import ProcessConfig, process
from .base_chunker import BaseChunker, CHUNK_SIZE, CHUNK_OVERLAP, LANGUAGE

TREE_SITTER_CHUNK_MAX_SIZE = 1000


class TreeSitterChunker(BaseChunker):
    def __init__(self, chunk_max_size: int = TREE_SITTER_CHUNK_MAX_SIZE, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP, language: str = LANGUAGE):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap, language=language)
        self.chunk_max_size = chunk_max_size

    def chunk(self, docs: list[Document]) -> list[Document]:
        config = ProcessConfig(
            language=self.language,
            structure=True,
            docstrings=True,
            chunk_max_size=self.chunk_max_size,
        )

        chunks = []

        for doc in docs:
            result = process(doc.page_content, config)
            for chunk in result.chunks:
                chunks.append(Document(
                    page_content=chunk.content,
                    metadata={
                        **doc.metadata,
                        "language": self.language,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "chunk_index": chunk.metadata.chunk_index,
                        "size_bytes": chunk.end_byte - chunk.start_byte,
                    },
                ))

        return chunks
