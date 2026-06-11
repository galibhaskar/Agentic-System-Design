from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

def build(chunks: list,
                       model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> Chroma:
    """Builds a Chroma vector store from the given document chunks using HuggingFace embeddings."""

    print(f"Building vector store with {len(chunks)} chunks...")

    embeddings = HuggingFaceEmbeddings(model_name=model_name)

    return Chroma.from_documents(chunks, embeddings)
