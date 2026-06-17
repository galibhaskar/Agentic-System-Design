from .test_plan import TestPlan


class TestPlanner:
    def __init__(self, test_run_id: str, docs_path: str, test_cases: list[dict], description: str = ""):
        self.test_run_id = test_run_id
        self.docs_path = docs_path
        self.test_cases = test_cases
        self.description = description
        self._chunker = None
        self._vector_store = None
        self._agent = None
        self._file_extension = ".py"

    def with_chunker(self, chunker) -> "TestPlanner":
        self._chunker = chunker
        return self

    def with_vector_store(self, vector_store) -> "TestPlanner":
        self._vector_store = vector_store
        return self

    def with_agent(self, agent) -> "TestPlanner":
        self._agent = agent
        return self

    def with_file_extension(self, extension: str) -> "TestPlanner":
        self._file_extension = extension
        return self

    def build(self) -> TestPlan:
        if not self._chunker:
            raise ValueError("Chunker is required. Call with_chunker() before build().")
        if not self._vector_store:
            raise ValueError("Vector store is required. Call with_vector_store() before build().")
        if not self._agent:
            raise ValueError("Agent is required. Call with_agent() before build().")

        return TestPlan(
            test_run_id=self.test_run_id,
            docs_path=self.docs_path,
            test_cases=self.test_cases,
            chunker=self._chunker,
            vector_store=self._vector_store,
            agent=self._agent,
            file_extension=self._file_extension,
            description=self.description,
        )
