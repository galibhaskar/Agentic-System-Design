# Day 3 Learnings

1. Types of RAGs:
    - Semantic RAG
    - Lexical RAG
    - Graph RAG
    - [Hybrid RAG](../week1/hybrid_rag.py) 

Refer to [Types of RAGs](./Types_of_RAG.md) for more details.

---

2. RAG evaluation Metrics:
    - Precision@k
    - Recall@k
    - Mean Reciprocal Rank (MRR)
    - Normalized Discounted Cumulative Gain (NDCG)
    - Faithfulness
    - Answer Relevance
    - Factual Correctness

Refer to [RAG Evaluation Metrics](./RAG_Evaluation_Metrics.md) for more details.

--- 

Notes:
- Hybrid RAG: Multiple Retrievers + Fusion(RRF) + Re-ranking (EnsembleRetriever with weights)

- Evaluation Metrics: Use LLM as judge to evaluate the metrics.
    - Libraries: RAGAS(Retrieval Augmented Generation Assessment), DeepEval, Langsmith,....

- Ranking:
    - Retrieval Ranking: DBs order the chunks using BM25, cosine similarity, etc.
    - Fusion Ranking: Combines the rankings from multiple retrievers by assigning scores based on their ranks and fusing them together. Handles duplicates as well.
        - RRF (Reciprocal Rank Fusion):
        - - score(doc) = sum(1 / (k + rank_i(doc))) for i in retrievers 
            - where k is a smoothingconstant (often set to 60) to dampen the influence of lower-ranked documents, and 
            - rank_i(doc) is the rank of the document in the i-th retriever's results.
        
        - Weighted Scored Fusion:
            - - score(doc) = alpha * bm25_score(doc) + beta * cosine_similarity_score(doc) + gamma * other_retriever_score(doc)
            - - where alpha, beta, and gamma are weights assigned to each retriever's score.


    - Re-ranking: reads each (query, document) pair and assigns Relevance score and re-ranks for priority using LLM.
        - - reads the retrieved doc using LLM. 
        - Cross Encoders: BGE Reranker, Cohere Reranker, MonoT5, etc. (takes query and doc as input and gives relevance score as output)

        


