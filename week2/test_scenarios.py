import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))         # week2/
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # project root

from helpers import load_env_vars
load_env_vars.load()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from chunkers import ASTChunker, RecursiveChunker
from vector_stores import SemanticVectorStore, LexicalVectorStore, HybridVectorStore, GraphVectorStore
from vector_stores.graph_vector_store import GraphDocument, Entities
from agents import GroqAgent
from runners import TestPlanner
from golden_dataset import TEST_CASES

# ---------------------------------------------------------------------------
# Paths and shared defaults
# ---------------------------------------------------------------------------

DOCS_PATH = str(Path(__file__).resolve().parent.parent / "datasources" / "sample_project")

HF_EMBEDDINGS  = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
OPENAI_EMBEDDINGS = OpenAIEmbeddings(model="text-embedding-3-small")

GRAPH_DEPTH = 2


# ---------------------------------------------------------------------------
# Graph extractor helper
# ---------------------------------------------------------------------------

class _StructuredExtractor:
    def __init__(self, llm, schema):
        self._chain = llm.with_structured_output(schema)

    def invoke(self, input: dict) -> dict:
        result = self._chain.invoke(input["messages"])
        return {"structured_response": result}


def _graph_store(depth: int = GRAPH_DEPTH) -> GraphVectorStore:
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    return GraphVectorStore(
        relationship_extractor=_StructuredExtractor(llm, GraphDocument),
        entity_extractor=_StructuredExtractor(llm, Entities),
        depth=depth,
    )


# ---------------------------------------------------------------------------
# Base planner helper
# ---------------------------------------------------------------------------

def _plan(test_run_id: str, description: str) -> TestPlanner:
    return TestPlanner(
        test_run_id=test_run_id,
        docs_path=DOCS_PATH,
        test_cases=TEST_CASES,
        description=description,
    ).with_agent(GroqAgent())


# ---------------------------------------------------------------------------
# All scenarios
# ---------------------------------------------------------------------------

def all_plans() -> list:
    graph = _graph_store()

    return [

        # 1. Semantic, chunk=256, k=4
        _plan("semantic-hf-256-k4", "Semantic | HuggingFace | chunk=256 | k=4")
        .with_chunker(RecursiveChunker(chunk_size=256))
        .with_vector_store(SemanticVectorStore(embeddings=HF_EMBEDDINGS, top_k=4))
        .build(),

        # 2. Semantic, chunk=1500, k=4
        _plan("semantic-hf-1500-k4", "Semantic | HuggingFace | chunk=1500 | k=4")
        .with_chunker(RecursiveChunker(chunk_size=1500))
        .with_vector_store(SemanticVectorStore(embeddings=HF_EMBEDDINGS, top_k=4))
        .build(),

        # 3. Semantic, chunk=1500, k=1
        _plan("semantic-hf-1500-k1", "Semantic | HuggingFace | chunk=1500 | k=1")
        .with_chunker(RecursiveChunker(chunk_size=1500))
        .with_vector_store(SemanticVectorStore(embeddings=HF_EMBEDDINGS, top_k=1))
        .build(),

        # 4. AST chunks, k=1
        _plan("semantic-ast-k1", "Semantic AST | HuggingFace | AST chunks | k=1")
        .with_chunker(ASTChunker())
        .with_vector_store(SemanticVectorStore(embeddings=HF_EMBEDDINGS, top_k=1))
        .build(),

        # 5. BM25, chunk=256, k=4
        _plan("lexical-bm25-256-k4", "Lexical BM25 | chunk=256 | k=4")
        .with_chunker(RecursiveChunker(chunk_size=256))
        .with_vector_store(LexicalVectorStore(top_k=4))
        .build(),

        # 6. Hybrid (HuggingFace + BM25), chunk=256, w=0.5/0.5
        _plan("hybrid-hf-bm25-256-w50", "Hybrid | HuggingFace + BM25 | chunk=256 | w=0.5/0.5")
        .with_chunker(RecursiveChunker(chunk_size=256))
        .with_vector_store(HybridVectorStore(
            stores=[SemanticVectorStore(embeddings=HF_EMBEDDINGS), LexicalVectorStore()],
            weights=[0.5, 0.5],
        ))
        .build(),

        # 7. Hybrid (OpenAI + BM25), chunk=256, w=0.5/0.5
        _plan("hybrid-openai-bm25-256-w50", "Hybrid | OpenAI + BM25 | chunk=256 | w=0.5/0.5")
        .with_chunker(RecursiveChunker(chunk_size=256))
        .with_vector_store(HybridVectorStore(
            stores=[SemanticVectorStore(embeddings=OPENAI_EMBEDDINGS), LexicalVectorStore()],
            weights=[0.5, 0.5],
        ))
        .build(),

        # 8. Hybrid (OpenAI + BM25), chunk=1500, w=0.5/0.5
        _plan("hybrid-openai-bm25-1500-w50", "Hybrid | OpenAI + BM25 | chunk=1500 | w=0.5/0.5")
        .with_chunker(RecursiveChunker(chunk_size=1500))
        .with_vector_store(HybridVectorStore(
            stores=[SemanticVectorStore(embeddings=OPENAI_EMBEDDINGS), LexicalVectorStore()],
            weights=[0.5, 0.5],
        ))
        .build(),

        # 9. GraphRAG, depth=2
        _plan("graph-rag-depth2", "Graph RAG | ASTChunker | depth=2")
        .with_chunker(ASTChunker())
        .with_vector_store(graph)
        .build(),

        # 10. Hybrid (Semantic + Lexical + Graph), chunk=256, w=equal
        _plan("hybrid-semantic-lexical-graph-256", "Hybrid | HuggingFace + BM25 + Graph | chunk=256 | w=equal")
        .with_chunker(RecursiveChunker(chunk_size=256))
        .with_vector_store(HybridVectorStore(
            stores=[SemanticVectorStore(embeddings=HF_EMBEDDINGS), LexicalVectorStore(), graph],
            weights=[1/3, 1/3, 1/3],
        ))
        .build(),

        # 11. Hybrid (Lexical + Graph), chunk=256, w=0.5/0.5
        _plan("hybrid-lexical-graph-256", "Hybrid | BM25 + Graph | chunk=256 | w=0.5/0.5")
        .with_chunker(RecursiveChunker(chunk_size=256))
        .with_vector_store(HybridVectorStore(
            stores=[LexicalVectorStore(), graph],
            weights=[0.5, 0.5],
        ))
        .build(),

        # 12. Hybrid (Semantic + Graph), chunk=256, w=0.5/0.5
        _plan("hybrid-semantic-graph-256", "Hybrid | HuggingFace + Graph | chunk=256 | w=0.5/0.5")
        .with_chunker(RecursiveChunker(chunk_size=256))
        .with_vector_store(HybridVectorStore(
            stores=[SemanticVectorStore(embeddings=HF_EMBEDDINGS), graph],
            weights=[0.5, 0.5],
        ))
        .build(),

    ]


# ---------------------------------------------------------------------------
# Entry point — run all plans or a specific plan by ID
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from runners import RagasEvaluationRunner

    plans = all_plans()
    runner = RagasEvaluationRunner()

    if len(sys.argv) > 1:
        plan_id = sys.argv[1]
        matched = [p for p in plans if p.test_run_id == plan_id]
        if not matched:
            print(f"No plan found with ID '{plan_id}'. Available plans:")
            for p in plans:
                print(f"  {p.test_run_id}")
            sys.exit(1)
        plans_to_run = matched
    else:
        plans_to_run = plans

    print(f"\nRunning {len(plans_to_run)} test plan(s) with Ragas...\n")
    all_results = []
    for p in plans_to_run:
        try:
            result = runner.run(p)
            all_results.append(result)
        except Exception as e:
            print(f"[{p.test_run_id}] FAILED: {e}")

    if all_results:
        runner.save_summary_table(all_results)

    print("\nDone. Results saved to week2/results/")
