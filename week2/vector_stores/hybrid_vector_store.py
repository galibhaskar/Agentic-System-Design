from langchain_core.documents import Document
from langchain_classic.retrievers import EnsembleRetriever
from .base_vector_store import BaseVectorStore, EMBEDDING_MODEL, TOP_K


class HybridVectorStore(BaseVectorStore):
    tool_name = "hybrid_search_codebase"
    tool_description = "Search the codebase by combining multiple retrieval strategies. Best for broad queries where both semantic meaning and exact terms matter."

    def __init__(
        self,
        stores: list[BaseVectorStore],
        weights: list[float] = None,
        embedding_model: str = EMBEDDING_MODEL,
        top_k: int = TOP_K,
    ):
        super().__init__(embedding_model=embedding_model, top_k=top_k)
        self.stores = stores
        self.weights = weights or [1.0 / len(stores)] * len(stores)

    def build(self, chunks: list[Document]) -> None:
        for store in self.stores:
            store.build(chunks)

    def as_retriever(self, k: int = TOP_K) -> EnsembleRetriever:
        retrievers = [store.as_retriever(k=k) for store in self.stores]
        return EnsembleRetriever(retrievers=retrievers, weights=self.weights)
