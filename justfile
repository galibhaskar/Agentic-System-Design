default:
    @just --list

run:
    PYTHONPATH=. uv run python main.py

rag:
    PYTHONPATH=. uv run python week1/semantic_rag.py

rag_ast:
    PYTHONPATH=. uv run python week1/semantic_rag_ast.py

lexical_rag:
    PYTHONPATH=. uv run python week1/lexical_rag.py

semantic_rag:
    PYTHONPATH=. uv run python week1/lexical_rag.py

tree_sitter:
    PYTHONPATH=. uv run python week1/tree_sitter_demo.py

semantic_rag_tree_sitter:
    PYTHONPATH=. uv run python week1/semantic_rag_tree_sitter.py

sync:
    uv sync
