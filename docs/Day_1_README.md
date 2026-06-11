### Day-1 Learnings:

1. RAG (Retrieval Augmented Generation):
`Docs -> Chunk -> Embed -> Store -> Retrieve -> Generate`

---
2. Semantic RAG:
   - Uses vector databases to store and retrieve relevant information based on cosine similarity.

   Semantic RAG Implementation: [week1/semantic_rag.py](../week1/semantic_rag.py)
---
3. RecursiveCharacterTextSplitter (Python)

- Refer to [RecursiveCharacterTextSplitter](https://python.langchain.com/en/latest/modules/indexes/text_splitters/examples/recursive_character_text_splitter.html) for more details.

- Flow:
   ```
   Try splitting by "class"
      ↓
   Still too big?
      ↓
   Try splitting by "def"
      ↓
   Still too big?
      ↓
   Try splitting by blank lines
      ↓
   Still too big?
      ↓
   Try splitting by newlines
      ↓
   Still too big?
      ↓
   Split by characters
   
   ```

---
4. Tracing in LangSmith:
   - https://smith.langchain.com/

   Tips:
   - create workspace and project in langsmith.
   - add params(tracing, endpoint, api_key, project_name) to .env file

---
5. Limiting model and tool calls of the agent:
   - Use middlewares to limit the number of calls to the model and tools.
   
   - References:
    - https://reference.langchain.com/python/langchain/agents/middleware/model_call_limit/ModelCallLimitMiddleware

    - https://reference.langchain.com/python/langchain/agents/middleware/tool_call_limit/ToolCallLimitMiddleware

    - Other middlewares: https://reference.langchain.com/python/langchain/agents/middleware/