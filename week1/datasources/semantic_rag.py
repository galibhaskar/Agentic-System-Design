from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.messages import ChatMessage, SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.tools.retriever import create_retriever_tool
from langchain.agents import create_agent
from pathlib import Path
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHUNK_SIZE = 256
CHUNK_OVERLAP = 32


def load_all_docs(repo_path):
    docs = []

    for path in Path(repo_path).rglob("*.py"):
        if path.is_file():
            # Ensure we can read the file
            content = path.read_text(encoding="utf-8", errors="ignore")

            docs.append(Document(content=content,
                        metadata={"source": str(path)}))

    return docs


def chunk_docs(docs: list[Document]) -> list:
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language="python",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP)

    return text_splitter.split_documents(docs)


def build_vector_store(chunks: list) -> Chroma:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2")

    return Chroma.from_documents(chunks, embeddings)


def build_agent(vector_store: Chroma) -> create_agent:
    search_tool = create_retriever_tool(
        vector_store.as_retriever(),
        name="code_search",
        description="Useful for searching the codebase for relevant information.")

    llm_instance = ChatGroq(api_key=GROQ_API_KEY)

    system_message = SystemMessage(
        content="You are a senior engineer. Always use search_codebase before answering. Reference specific file and function names. If not found say 'I could not find that in the codebase'.`")

    return create_agent(
        llm=llm_instance,
        tools=[search_tool],
        system_message=system_message)


if __name__ == "__main__":
    # Load and chunk documents
    docs = load_all_docs("./datasources")
    chunks = chunk_docs(docs)

    print(type(chunks), len(chunks))

    # Build vector store and agent
    vector_store = build_vector_store(chunks)
    agent = build_agent(vector_store)

    while True:
        query = input("Ask a question about the codebase: ")

        if query.lower() in ["exit", "quit"]:
            break

        # for chunk in agent.stream({"messages": [HumanMessage(content=query)]},
        #                           stream_mode="values"):
        #     print(chunk, end="", flush=True)
        # print("\n---\n")
