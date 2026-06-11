import ast
from pathlib import Path
from helpers import doc_loader, vector_store
from langchain.agents import create_agent
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_core.messages import ChatMessage, SystemMessage, HumanMessage
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain.agents.middleware import ToolCallLimitMiddleware, ModelCallLimitMiddleware
from helpers import load_env_vars
from tree_sitter_demo import build_chunks

# checkout the helper files to see the env var loading
load_env_vars.load()

def build_agent(vector_store: Chroma) -> create_agent:
    """Builds a retrieval-augmented generation agent using the given vector store."""

    search_codebase = create_retriever_tool(
        vector_store.as_retriever(search_kwargs={"k": 4}),
        name="search_codebase",
        description="Searches the codebase for relevant code snippets based on a query. Useful for finding existing code that can be reused or adapted.")

    tools = [search_codebase]

    agent = create_agent(
        tools=tools,
        model=ChatGroq(model="llama-3.3-70b-versatile", temperature=0),
        system_prompt=SystemMessage(
            content="You are an assistant that helps developers understand and work with a Python codebase. You can search the codebase for relevant snippets to answer questions or help with coding tasks."),
        middleware=[
            ToolCallLimitMiddleware(run_limit=2),
            ModelCallLimitMiddleware(run_limit=10)]
    )

    return agent


if __name__ == "__main__":
    # load docs
    docs = doc_loader.load_all_docs(repo_path=Path(
        __file__).resolve().parent / "datasources", file_extension=".py")
    print(f"Loaded {len(docs)} documents.")

    # chunk docs
    chunks = build_chunks(docs)
    print(f"Created {len(chunks)} chunks using TreeSitter.")

    if not chunks:
        print("No chunks created. Exiting.")
        exit()

    # build vector store
    vector_store = vector_store.build(chunks)
    print("Built vector store.")

    # build agent
    agent = build_agent(vector_store)
    print("Built agent.")

    while True:
        query = input(
            "\nEnter your question about the codebase (or 'exit' to quit): ")

        if query.lower() == "exit":
            break

        for chunk in agent.stream({"messages": [HumanMessage(content=query)]}, stream_mode="values", version="v2"):
            last_message = chunk['data']['messages'][-1].content
            
        print(last_message, end="", flush=True)
