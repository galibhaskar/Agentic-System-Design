from dataclasses import dataclass, field
from typing import Any


@dataclass
class TestPlan:
    test_run_id: str
    docs_path: str
    test_cases: list[dict]
    chunker: Any = None
    vector_store: Any = None
    agent: Any = None
    file_extension: str = ".py"
    description: str = ""
