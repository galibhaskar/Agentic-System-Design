# Day 5 Learnings:

1. Agentic RAG:
    - If an agent decides which retriever to use based on the query using LLM.
    - Implementation: [Agentic RAG](../week2/agentic_rag_demo.py)

---

2. HyDE RAG Agent:
    - Hypothetical Document Embedding(HyDE) paraphrases the user query for better retrieval.

    - core idea:
        - Don't embed the raw user query.
        - generate plausible hypothetical document(s).
        - Embed the hypothetical docs and fetch the nearest neighbors from the vector store.
        - This can help bridge the gap between the user's language and the language used in the agent.

    - Implementation: [HyDE RAG Agent](../week2/hyde_rag_demo.py)

    - Research Paper: [HyDE: Hypothetical Document Embeddings Improve Retrieval-Augmented Generation]( https://arxiv.org/abs/2212.10496)

---

3. RAPTOR(Recursive Abstractive Processing for Tree-Organized Retrieval):
    - Advanced RAG indexing technique that builds heirarchical retrieval structures.
    - **Ingestion**:
        - **Leaf Chunks**: The data is initially broken down into small, manageable chunks (leaf nodes).
        - **Recursive Abstraction**: These chunks are then recursively abstracted into higher-level summaries using LLM, creating a tree-like structure.
    - **Retrieval**: 
        - During retrieval, the system can navigate this tree structure to efficiently find relevant information, starting from the most abstract level(root) and drilling down to the specific details as needed.
        - The entire tree structure is flattened into a single, vast pool of text nodes. The system calculates cosine similarity against everything at once, fetching the absolute top-k most relevant items.
    - Research Paper: [RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval](https://arxiv.org/abs/2401.18059)

---

4. Vectorless RAG:
    - Retrieval without vector databases.
    - Uses LLMs to directly reason over the corpus and fetch relevant information (**__NO EMBEDDINGS, SIMILARITY SEARCH, OR VECTOR DBs__**).
    - **Tree Building**:
        - builds a tree index of titles + LLM-generated summaries of the documents.
    - **Query Processing**:
        - agent reads the summaries, title and reason through to find the nodes that're relevant to the query and fetches the corresponding documents.

    - Library: [PageIndex - Vectorless RAG](https://github.com/VectifyAI/PageIndex)

    - Research Paper: [Vectorless Retrieval-Augmented Generation](https://arxiv.org/abs/2401.10092)

---

5. Context Engineering:
    