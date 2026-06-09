default:
    @just --list

run:
    uv run python main.py

rag:
    uv run python week1/semantic_rag.py

sync:
    uv sync
