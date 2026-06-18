import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))         # week2/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # project root

from helpers import load_env_vars, doc_loader
load_env_vars.load()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage

from chunkers import ASTChunker, RecursiveChunker
from vector_stores import SemanticVectorStore, LexicalVectorStore, GraphVectorStore
from vector_stores.graph_vector_store import GraphDocument, Entities
from agents import AgenticRAGAgent
from langchain_groq import ChatGroq

DOCS_PATH = Path(__file__).resolve().parent.parent / "datasources" / "sample_project"
CHUNK_SIZE = 1500


# ---------------------------------------------------------------------------
# Graph extractor helper
# ---------------------------------------------------------------------------

class _StructuredExtractor:
    def __init__(self, llm, schema):
        self._chain = llm.with_structured_output(schema)

    def invoke(self, input: dict) -> dict:
        result = self._chain.invoke(input["messages"])
        return {"structured_response": result}


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build_agentic_rag():
    # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

    # 1. Load and chunk docs
    print("Loading docs...")
    docs = doc_loader.load_all_docs(str(DOCS_PATH), file_extension=".py")

    print(f"Chunking {len(docs)} docs...")
    ast_chunks = ASTChunker().chunk(docs)
    recursive_chunks = RecursiveChunker(chunk_size=CHUNK_SIZE).chunk(docs)

    # 2. Build vector stores
    print("Building semantic vector store...")
    semantic_store = SemanticVectorStore(
        embeddings=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2"),
        top_k=4,
    )
    semantic_store.build(recursive_chunks)

    print("Building lexical vector store...")
    lexical_store = LexicalVectorStore(top_k=4)
    lexical_store.build(recursive_chunks)

    # print("Building graph vector store...")
    # graph_store = GraphVectorStore(
    #     relationship_extractor=_StructuredExtractor(llm, GraphDocument),
    #     entity_extractor=_StructuredExtractor(llm, Entities),
    #     depth=2,
    # )
    # graph_store.build(ast_chunks)

    # 3. Create retriever tools
    retriever_tools = [
        semantic_store.as_retriever_tool(),
        lexical_store.as_retriever_tool(),
        # graph_store.as_retriever_tool(),
    ]

    # 4. Build agentic RAG agent
    print("Building agentic RAG agent...")
    agent_wrapper = AgenticRAGAgent(retriever_tools=retriever_tools)
    agent = agent_wrapper.build()

    return agent, agent_wrapper


# ---------------------------------------------------------------------------
# Main — interactive query loop
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    agent, agent_wrapper = build_agentic_rag()
    print("\nAgentic RAG ready. The router will pick the right retriever per query.")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("Ask a question about the codebase: ").strip()
        if query.lower() in ("exit", "quit"):
            break
        if not query:
            continue

        answer, context = agent_wrapper.agent_run(agent, query)
        print(f"\nAnswer:\n{answer}\n")
        print(f"Context:\n{context}\n")
