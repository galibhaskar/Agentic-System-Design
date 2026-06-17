from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import ConfigDict
from rank_bm25 import BM25Okapi
from .base_vector_store import BaseVectorStore, EMBEDDING_MODEL, TOP_K


class _BM25Retriever(BaseRetriever):
    docs: list[Document]
    bm25: object
    k: int = TOP_K

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.k]
        return [self.docs[i] for i in top_indices]


class LexicalVectorStore(BaseVectorStore):
    tool_name = "lexical_search_codebase"
    tool_description = "Search the codebase using keyword matching (BM25). Best for exact function names, variable names, or specific terms."

    def __init__(self, embedding_model: str = EMBEDDING_MODEL, top_k: int = TOP_K):
        super().__init__(embedding_model=embedding_model, top_k=top_k)
        self._retriever: _BM25Retriever = None

    def build(self, chunks: list[Document]) -> None:
        tokenized = [doc.page_content.lower().split() for doc in chunks]
        self._retriever = _BM25Retriever(docs=chunks, bm25=BM25Okapi(tokenized), k=self.top_k)

    def as_retriever(self, k: int = TOP_K) -> _BM25Retriever:
        self._retriever.k = k
        return self._retriever
