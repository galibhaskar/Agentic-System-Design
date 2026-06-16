from helpers import load_env_vars, doc_loader
from langchain_groq import ChatGroq
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_core.messages import ChatMessage, SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools.retriever import create_retriever_tool
from langchain.agents import create_agent
from pathlib import Path
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware
from rank_bm25 import BM25Okapi
from langchain_core.retrievers import BaseRetriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import ConfigDict
import argparse
import os

load_env_vars.load()

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def chunk_code(docs: list[Document]) -> list:
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP)

    return splitter.split_documents(docs)


def build_vector_retriever(chunks: list) -> Chroma:
    print(f"Building vector store with {len(chunks)} chunks...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2")

    return Chroma.from_documents(chunks, embeddings).as_retriever(search_kwargs={"k": 4})


class BM25Retriever(BaseRetriever):
    docs: list[Document]
    bm25: object
    k: int = 4

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        tokens = query.lower().split()

        scores = self.bm25.get_scores(tokens)

        top_k_indices = sorted(
            range(len(scores)), key=lambda i: scores[i], reverse=True)[:self.k]

        return [self.docs[i] for i in top_k_indices]

def build_bm25_retriever(chunks: list) -> BM25Retriever:
    tokenized_corpus = [doc.page_content.lower().split() for doc in chunks]

    bm25 = BM25Okapi(tokenized_corpus)

    return BM25Retriever(docs=chunks, bm25=bm25)

def build_hybrid_retriever(chunks: list):
    semantic_retriever = build_vector_retriever(chunks)

    bm25_retriever = build_bm25_retriever(chunks)

    # Ensemble retriever combines multiple retrievers with specified weights. It uses RRF (Reciprocal Rank Fusion) to aggregate results, and re-ranks them based on the combined scores from both retrievers. Adjusting the weights allows you to control the influence of each retriever in the final results.

    # 0.5, 0.5 -> equal weight to both retrievers
    # 0.7, 0.3 -> more of semantic chunks for codebases with more complex logic and less documentation.
    # 0.3, 0.7 -> more of keyword matching chunks for documentation heavy codebases.

    return EnsembleRetriever(retrievers=[semantic_retriever, bm25_retriever], weights=[0.5, 0.5])


def build_agent(retriever):
    retriever_tool = create_retriever_tool(retriever,
                                 name="search_codebase",
                                 description="Search the codebase for relevant functions, classes, or logic.")

    agent = create_agent(
        tools=[retriever_tool],
       model=ChatGroq(model="llama-3.3-70b-versatile", temperature=0),
        system_prompt=(
            "You are a senior engineer. Always use search_codebase before answering. "
            "Reference specific file and function names. "
            "If not found say 'I could not find that in the codebase'."
        ),
        middleware=[
            ToolCallLimitMiddleware(run_limit=5),
            ModelCallLimitMiddleware(run_limit=10)]
    )

    return agent


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-path", type=str, required=True, help="Path to the codebase to index")
    args = parser.parse_args()

    docs = doc_loader.load_all_docs(repo_path=Path(args.repo_path).resolve())

    print(f"Loaded {len(docs)} documents from the codebase.")

    chunks = chunk_code(docs)

    print(f"Created {len(chunks)} chunks from the documents.")

    if not chunks:
        print("No code chunks were created. Please check the document loading and chunking process.")
        exit(1)

    print(f"Total chunks created: {len(chunks)}")

    retriever = build_hybrid_retriever(chunks)

    print("Retrievers built successfully. Starting agent...")

    agent = build_agent(retriever)

    print("Agent is ready to answer questions about the codebase.")

    while True:
        query = input(
            "Enter your question about the codebase (or 'exit' to quit): ")

        if query.lower() == "exit":
            break

        for step in agent.stream({"messages": [
            HumanMessage(content=query)
        ]}, stream_mode="values"):
            last_message = step["messages"][-1].content

        print(f"Agent response: {last_message}")
