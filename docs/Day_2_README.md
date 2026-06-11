# Day-2 Learnings

1. Introduction to AST (Abstract Syntax Tree)
- Usecase: for code parsing and understanding the structure of code.
- AST-Based Chunking Flow
    ```
    Source Code → AST Tree → Find Classes/Functions → Extract Source Code → Create Chunks → Embed & Store
    ```
- AST API in Python: `ast` module.
    - `ast.parse()`: Parses Python source code into an AST.
    - `ast.dump()`: Returns a string representation of the AST
    - `ast.walk()`: Traverses the AST and yields all nodes in the tree.
    - `ast.iter_child_nodes()`: Iterates over the child nodes of a given AST node.
    - `ast.get_source_segment()`: Retrieves the source code segment corresponding to a given AST node.

---

2. Semantic RAG using AST:
- Instead of chunking code based on characters or lines, we can use AST to chunk code based on logical units such as classes and functions.
- This allows us to create more meaningful chunks that are easier for the model to understand and retrieve relevant information from.

Refer to [AST RAG Implementation](../week1/semantic_rag_ast.py) for more details.

---
3. Introduction to BM25:
- BM25 is uses exact keyword matching to retrieve relevant information from a corpus of documents.
- BM25 (Best Matching 25) = Inverted Index + Ranking Algorithm.
- BM25 score  =  Term Frequency  +  Word Rarity(IDF)  -  Length Penalty

Refer to [BM25 Implementation](../week1/bm25_demo.py) for more details.

---
4. Lexical RAG using BM25:
- Uses BM25 to retrieve relevant information based on exact keyword matching.
- **Neither exact match alone nor semantic match alone is sufficient for retrieval**.
- During Hybrid Retrieval, 
    - We use BM25 for exact match retrieval
    - We use vector database for semantic retrieval.
    - Other techniques of retrieval for different sources...like sql, elastic search, graphdb, etc.
    - Finally, combine the results and re-rank for best context to the query.

Refer to [Lexical RAG Implementation](../week1/lexical_rag.py) for more details.


---
## AST vs RecursiveCharacterTextSplitter:
| AST RAG | RecursiveCharacterTextSplitter |
| --- | --- |
| Understands the structure of code and chunks it based on logical units. | Uses a recursive approach to chunk code based on characters, lines, and blank lines. |
| Creates more meaningful chunks that are easier for the model to understand. | Creates chunks based on character-level boundaries. |

---

## TreeSitter:
- TreeSitter is a parser generator tool and an incremental parsing library.

- Checkout: [tree-sitter-demo](../week1/tree_sitter_demo.py)

- Reference: https://github.com/kreuzberg-dev/tree-sitter-language-pack