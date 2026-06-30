# Day 6 Learnings:

1. Context Engineering:
    - Context is limited in LLMs 
    - Components:
        - System prompt
        - User query
        - Retrieved context
        - Tool registry and outputs
        - Conversation history
    - Strategies:
        - Context Expansion: 
            - **use case**: __how do we get more information in context__.
            - Query Rewriting, HyDE, Multi-Hop retrieval, Graph Expansion etc.

        - Context Selection: 
            - **use case**: __too much information, what do we keep it__.
            - Top K, Similarity thresholds, Relevance filtering, and memory retrieval techniques(pulling long-term memories based on context).

        - **Context Compression**: 
            - **use case**: __still too large, how do we reduce it__.
            - Summarization, factual extraction, hierarchical summarization, context distillation.

        - **Context Pruning**: Removing less relevant or redundant information from the context to make room for more important details.
        - 

2. Lost in Middle Problem:
    - Recency Effect: Due to transformer architecture, most recent chunks attend to new chunks.
    - Primary Effect: Default learning behavior during training, as most important instructions come in the beginning of the prompt.

3. Memory:
    - Short-term memory: Limited to the context window of the LLM.
    - Long-term memory: Can be implemented using external storage solutions, such as databases or knowledge graphs, to store information that can be retrieved and used in future interactions.

---

## Short-Term Memory Management Techniques:
- Sliding Window Memory
- Rolling Summary
- Message Trimming
- Semantic Recall
- State Extraction
- Hierarchical Summary

## Common Production Pattern
Most modern agentic systems combine multiple approaches. Relying on any single technique is rare. The most common hybrid pattern:
```
    Recent Messages          ← sliding window of last N turns
        +
    Running Summary          ← rolling compression of older turns
        +
    Retrieved Memories       ← semantic recall from vector store
        +
    Structured State         ← extracted user profile / preferences
```

Example: Keep the last 10 messages verbatim + a running conversation summary + relevant memories retrieved from history + user profile (name, goal, preferred language). This covers recency, compression, fuzzy recall, and structured facts - all in one context.

---

# Long-Term Memory Management Techniques:
- Semantic Memory
- Episodic Memory
- Procedural Memory
