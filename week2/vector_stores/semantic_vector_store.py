from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from .base_vector_store import BaseVectorStore, EMBEDDING_MODEL, TOP_K


class SemanticVectorStore(BaseVectorStore):
    tool_name = "semantic_search_codebase"
    tool_description = "Search the codebase using semantic similarity. Best for conceptual or meaning-based queries."

    def __init__(self, embeddings=None, embedding_model: str = EMBEDDING_MODEL, top_k: int = TOP_K):
        super().__init__(embedding_model=embedding_model, top_k=top_k)
        self._provided_embeddings = embeddings
        self._store: Chroma = None

    def build(self, chunks: list[Document]) -> None:
        embeddings = self._provided_embeddings or HuggingFaceEmbeddings(model_name=self.embedding_model)
        self._store = Chroma.from_documents(chunks, embeddings)

    def as_retriever(self, k: int = TOP_K):
        return self._store.as_retriever(search_kwargs={"k": k})
