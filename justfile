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

hybrid_rag:
    PYTHONPATH=. uv run python week1/hybrid_rag.py --repo-path datasources/sample_project

agentic_rag:
    PYTHONPATH=. uv run python week2/agentic_rag_demo.py

hyde_rag:
    PYTHONPATH=. uv run python week2/hyde_rag_demo.py

test_scenarios:
    PYTHONPATH=. uv run python week2/test_suit.py

run_plan plan_id:
    PYTHONPATH=. uv run python week2/test_suit.py {{plan_id}}

sync:
    uv sync
