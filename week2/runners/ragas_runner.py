import sys
import types

if "langchain_community.chat_models.vertexai" not in sys.modules:
    class _ChatVertexAI:
        pass
    _shim = types.ModuleType("langchain_community.chat_models.vertexai")
    _shim.ChatVertexAI = _ChatVertexAI
    sys.modules["langchain_community.chat_models.vertexai"] = _shim

from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.metrics._context_precision import LLMContextPrecisionWithReference
from ragas.metrics._context_recall import LLMContextRecall
from ragas.metrics._faithfulness import Faithfulness
from ragas.metrics._answer_relevance import AnswerRelevancy
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from .base_runner import BaseEvaluationRunner

DEFAULT_METRICS = [
    LLMContextPrecisionWithReference(),
    LLMContextRecall(),
    Faithfulness(),
    AnswerRelevancy(),
]

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
DEFAULT_JUDGE_MODEL = "llama-3.3-70b-versatile"


class RagasEvaluationRunner(BaseEvaluationRunner):
    def __init__(self, metrics: list = None, llm=None, embeddings=None):
        self.metrics = metrics or DEFAULT_METRICS
        self.llm = llm or LangchainLLMWrapper(
            ChatGroq(model=DEFAULT_JUDGE_MODEL, temperature=0)
        )
        self.embeddings = embeddings or LangchainEmbeddingsWrapper(
            HuggingFaceEmbeddings(model_name=DEFAULT_EMBEDDING_MODEL)
        )

    def evaluate(self, samples: list[dict]) -> dict:
        ragas_samples = [
            SingleTurnSample(
                user_input=s["question"],
                response=s["answer"],
                retrieved_contexts=s["context"],
                reference=s["reference"],
            )
            for s in samples
        ]

        dataset = EvaluationDataset(samples=ragas_samples)
        result = evaluate(
            dataset=dataset,
            metrics=self.metrics,
            llm=self.llm,
            embeddings=self.embeddings,
        )

        df = result.to_pandas()
        metric_cols = df.select_dtypes(include="number").columns.tolist()

        summary = {col: float(df[col].mean()) for col in metric_cols}
        per_sample = {
            i: {"score": float(df.iloc[i][metric_cols].mean())}
            for i in range(len(df))
        }

        return {"summary": summary, "per_sample": per_sample}
