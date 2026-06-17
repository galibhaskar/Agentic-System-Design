from openevals.llm import create_llm_as_judge
from openevals.prompts import CORRECTNESS_PROMPT
from .base_runner import BaseEvaluationRunner

DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.2


class OpenEvalsEvaluationRunner(BaseEvaluationRunner):
    def __init__(self, model: str = DEFAULT_MODEL, prompt=None, temperature: float = DEFAULT_TEMPERATURE):
        self.judge = create_llm_as_judge(
            model=model,
            prompt=prompt or CORRECTNESS_PROMPT,
            temperature=temperature,
        )

    def evaluate(self, samples: list[dict]) -> dict:
        per_sample = {}
        scores = []

        for i, s in enumerate(samples):
            result = self.judge(
                inputs={"question": s["question"]},
                outputs={"answer": s["answer"]},
                reference_outputs={"answer": s["reference"]},
            )
            score = result.get("score", 0)
            scores.append(score)
            per_sample[i] = {"score": score, "reasoning": result.get("comment", "")}

        avg = sum(scores) / len(scores) if scores else 0.0
        return {"summary": {"correctness": avg}, "per_sample": per_sample}
