import ast
from pathlib import Path
from helpers import doc_loader, vector_store
from langchain.agents import create_agent
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.messages import ChatMessage, SystemMessage, HumanMessage
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware
from helpers import load_env_vars
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from rank_bm25 import BM25Okapi
from pydantic import ConfigDict
from langchain_core.retrievers import BaseRetriever

# checkout the helper files to see the env var loading
load_env_vars.load()

CHUNK_SIZE = 500
CHUNK_OVERLAP = 32


def chunk_docs(docs: list[Document]) -> list:
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP)

    return splitter.split_documents(docs)

# ---------------------------------------------------------------------------
# BM25 INDEX — no embeddings, pure term frequency
# ---------------------------------------------------------------------------

class BM25Retriever(BaseRetriever):
    """Thin LangChain-compatible retriever backed by rank_bm25."""
    docs: list
    bm25: object
    k: int = 4

    class Config:
        arbitrary_types_allowed = True

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list:
        tokens = query.lower().split()
        scores = self.bm25.get_scores(tokens)

        print(f"BM25 scores for query '{query}': {scores}")

        top_indices = sorted(range(len(scores)),
                             key=lambda i: scores[i], reverse=True)[: self.k]
        return [self.docs[i] for i in top_indices]


def build_bm25_retriever(chunks: list) -> BM25Retriever:
    tokenized = [doc.page_content.lower().split() for doc in chunks]
    bm25 = BM25Okapi(tokenized)
    return BM25Retriever(docs=chunks, bm25=bm25)


def build_agent(retriever: BaseRetriever) -> create_agent:
    search_codebase = create_retriever_tool(
        retriever,
        name="search_codebase",
        description="Search the codebase for relevant snippets to answer questions or help with coding tasks.")

    return create_agent(
        tools=[search_codebase],
        model=ChatGroq(model="llama-3.3-70b-versatile", temperature=0),
        system_prompt=SystemMessage(
            content="You are an assistant that helps developers understand and work with a Python codebase. You can search the codebase for relevant snippets to answer questions or help with coding tasks."),
        middleware=[
            ToolCallLimitMiddleware(run_limit=2),
            ModelCallLimitMiddleware(run_limit=10)]
    )

if __name__ == "__main__":
    # load docs
    docs = doc_loader.load_all_docs(repo_path=Path(
        __file__).resolve().parent / "datasources", file_extension=".py")
    print(f"Loaded {len(docs)} documents.")

    # chunk docs
    chunks = chunk_docs(docs)
    print(f"Created {len(chunks)} chunks using Character Splitter.")

    if not chunks:
        print("No chunks created. Exiting.")
        exit()

    # build BM25 retriever
    retriever = build_bm25_retriever(chunks)
    print("Built BM25 retriever.")

    # build agent
    agent = build_agent(retriever)
    print("Built agent.")

    while True:
        query = input(
            "\nEnter your question about the codebase (or 'exit' to quit): ")

        if query.lower() == "exit":
            break
    
        for chunk in agent.stream(
            {"messages": [HumanMessage(content=query)]}, stream_mode="values", version="v2"):
            last_chunk = chunk['data']['messages'][-1].content

        print("Agent Response:")
        print(last_chunk, end="", flush=True)