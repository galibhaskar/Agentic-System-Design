from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
import json
from helpers import doc_loader
from .test_plan import TestPlan

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"

METRIC_DISPLAY = {
    "context_precision": "Precision",
    "context_recall": "Recall",
    "faithfulness": "Faithfulness",
    "answer_relevancy": "Relevancy",
}


class BaseEvaluationRunner(ABC):

    def run(self, test_plan: TestPlan) -> dict:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        samples = self._load_responses(test_plan.test_run_id)

        if samples:
            print(f"\n[{test_plan.test_run_id}] Loaded {len(samples)} cached responses — skipping agent inference.")
        else:
            print(f"\n[{test_plan.test_run_id}] Loading docs from {test_plan.docs_path}...")
            docs = doc_loader.load_all_docs(test_plan.docs_path, test_plan.file_extension)

            print(f"[{test_plan.test_run_id}] Chunking {len(docs)} docs...")
            chunks = test_plan.chunker.chunk(docs)

            print(f"[{test_plan.test_run_id}] Building vector store with {len(chunks)} chunks...")
            test_plan.vector_store.build(chunks)
            tool = test_plan.vector_store.as_retriever_tool(k=test_plan.vector_store.top_k)

            print(f"[{test_plan.test_run_id}] Building agent...")
            test_plan.agent.tools = [tool]
            agent = test_plan.agent.build()

            print(f"[{test_plan.test_run_id}] Running {len(test_plan.test_cases)} test cases...")
            samples = []
            for i, tc in enumerate(test_plan.test_cases, 1):
                print(f"  [{i}/{len(test_plan.test_cases)}] {tc['question'][:60]}...")
                answer, context = test_plan.agent.agent_run(agent, tc["question"])
                samples.append({
                    "question": tc["question"],
                    "answer": answer,
                    "context": context,
                    "reference": tc.get("reference", ""),
                })

            self._save_responses(test_plan, samples)

        print(f"[{test_plan.test_run_id}] Evaluating...")
        results = self.evaluate(samples)

        self._save_results(test_plan, results, samples)
        print(f"[{test_plan.test_run_id}] Done. Results saved to results/{test_plan.test_run_id}.md")
        return {"plan": test_plan, "summary": results.get("summary", {})}

    @abstractmethod
    def evaluate(self, samples: list[dict]) -> dict:
        ...

    def _responses_path(self, test_run_id: str) -> Path:
        return RESULTS_DIR / f"{test_run_id}_responses.json"

    def _load_responses(self, test_run_id: str) -> list[dict] | None:
        path = self._responses_path(test_run_id)
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            return data["samples"]
        return None

    def _save_responses(self, test_plan: TestPlan, samples: list[dict]) -> None:
        path = self._responses_path(test_plan.test_run_id)
        data = {
            "test_run_id": test_plan.test_run_id,
            "timestamp": datetime.now().isoformat(),
            "agent": type(test_plan.agent).__name__,
            "model": getattr(test_plan.agent, "model_name", "unknown"),
            "chunker": type(test_plan.chunker).__name__,
            "vector_store": type(test_plan.vector_store).__name__,
            "num_samples": len(samples),
            "samples": samples,
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"[{test_plan.test_run_id}] Responses saved to results/{test_plan.test_run_id}_responses.json")

    def save_summary_table(self, all_results: list[dict]) -> None:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        summary_path = RESULTS_DIR / "summary.md"

        metric_keys = list(METRIC_DISPLAY.keys())
        headers = ["Config", "Retrieval", "Precision", "Recall", "Faithfulness", "Relevancy"]
        sep = ["-" * len(h) for h in headers]

        lines = [
            "# Evaluation Summary",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "| " + " | ".join(headers) + " |",
            "| " + " | ".join(sep) + " |",
        ]

        for r in all_results:
            plan = r["plan"]
            summary = r["summary"]
            retrieval = type(plan.vector_store).__name__.replace("VectorStore", "")
            scores = [
                f"{summary[k]:.3f}" if k in summary else "N/A"
                for k in metric_keys
            ]
            lines.append(f"| {plan.description} | {retrieval} | " + " | ".join(scores) + " |")

        summary_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"\nSummary table saved to results/summary.md")

    def _save_results(self, test_plan: TestPlan, results: dict, samples: list[dict]) -> None:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = RESULTS_DIR / f"{test_plan.test_run_id}.md"

        chunker_name = type(test_plan.chunker).__name__
        store_name = type(test_plan.vector_store).__name__
        agent_name = type(test_plan.agent).__name__
        runner_name = type(self).__name__

        lines = [
            f"# Test Run: {test_plan.test_run_id}",
            f"",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
            f"**Runner:** {runner_name}  ",
            f"**Chunker:** {chunker_name}  ",
            f"**Vector Store:** {store_name}  ",
            f"**Agent:** {agent_name}  ",
        ]

        if test_plan.description:
            lines += ["", f"**Description:** {test_plan.description}  "]

        lines += ["", "## Evaluation Summary", ""]
        summary = results.get("summary", {})
        if summary:
            lines += ["| Metric | Score |", "|--------|-------|"]
            for col, score in summary.items():
                label = METRIC_DISPLAY.get(col, col)
                lines.append(f"| {label} | {score:.4f} |")
        else:
            lines.append("_No aggregate summary available._")

        lines += ["", "## Sample Results", ""]
        for i, sample in enumerate(samples, 1):
            score = results.get("per_sample", {}).get(i - 1, {}).get("score", "N/A")
            lines += [
                f"### {i}. {sample['question']}",
                f"",
                f"**Answer:** {sample['answer']}  ",
                f"",
                f"**Reference:** {sample['reference']}  ",
                f"",
                f"**Score:** {score}  ",
                f"",
                f"**Context gathered:**  ",
            ]
            for ctx in sample["context"]:
                lines.append(f"> {ctx[:300].replace(chr(10), ' ')}  ")
            lines.append("")
            lines.append("---")
            lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
