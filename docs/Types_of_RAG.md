# Types of RAG

-----------------------------------------------------
Type | Description | store | Ingestion Flow | Retrieval Flow 
--- | --- | --- | --- | ---
Semantic RAG | Semantic meaning using cosine similarity | vector databases like FAISS, Weaviate | ``docs -> chunk -> embed -> store`` | ``query -> embed -> cosine similarity -> retrieve``
Sparse RAG(Lexical RAG) | Lexical meaning using keyword matching | Elasticsearch, Solr | ``docs -> store as inverted index`` | ``query -> keyword matching -> retrieve``
Graph RAG | Knowledge graph representation | Graph databases like Neo4j, Amazon Neptune | ``docs -> extract entities/relations -> store as graph`` | ``query -> graph traversal -> retrieve``
Hybrid RAG | Combines semantic and sparse retrieval | Both vector and keyword-based databases | ``docs -> chunk -> embed -> store in vector DB + store in inverted index`` | ``query -> embed + keyword matching -> retrieve from both -> fusion using Reciprocal Rank Fusion to combine results -> re-rank using cross-encoder or LLM``
-----------------------------------------------------