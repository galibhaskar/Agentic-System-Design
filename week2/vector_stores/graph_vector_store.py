import networkx as nx
from pydantic import BaseModel, Field, ConfigDict
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from .base_vector_store import BaseVectorStore, EMBEDDING_MODEL, TOP_K

GRAPH_DEPTH = 2


# ---------------------------------------------------------------------------
# Structured output schemas
# ---------------------------------------------------------------------------

class CodeRelationship(BaseModel):
    subject: str = Field(description="Class, function, module, or file path")
    predicate: str = Field(description="Relationship type (e.g., DEFINES, IMPORTS, USES, CALLS, DEPENDS_ON, INHERITS_FROM)")
    obj: str = Field(description="Target class, function, module, or file path")


class GraphDocument(BaseModel):
    relationships: list[CodeRelationship] = Field(description="All code relationships extracted from the source file")


class Entities(BaseModel):
    names: list[str] = Field(description="Code entities in the query: class names, function names, modules, file paths")


# ---------------------------------------------------------------------------
# Graph helpers
# ---------------------------------------------------------------------------

def _extract_relationships(relationship_extractor, chunks: list[Document]) -> list[CodeRelationship]:
    relationships = []
    for doc in chunks:
        rel_path = doc.metadata.get("source", "unknown")
        result = relationship_extractor.invoke(
            {"messages": [{"role": "user", "content": f"File: {rel_path}\n\n{doc.page_content}"}]}
        )
        relationships.extend(result["structured_response"].relationships)
    return relationships


def _build_graph(relationships: list[CodeRelationship]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for r in relationships:
        graph.add_edge(r.subject.strip(), r.obj.strip(), relation=r.predicate)
    return graph


def _match_nodes(graph: nx.DiGraph, entity: str) -> list[str]:
    needle = entity.strip().lower()
    return [node for node in graph.nodes() if needle in node.lower() or node.lower() in needle]


def _graph_retrieve(graph: nx.DiGraph, entity_extractor, query: str, depth: int) -> str:
    result = entity_extractor.invoke({"messages": [{"role": "user", "content": query}]})
    entities = result["structured_response"].names

    relationships = []
    for entity in entities:
        for node in _match_nodes(graph, entity):
            neighbourhood = nx.ego_graph(graph, node, radius=depth, undirected=True)
            for source, target, data in neighbourhood.edges(data=True):
                relationships.append(f"{source} -[{data['relation']}]-> {target}")

    if not relationships:
        return "No relevant graph data found."
    return "Knowledge Graph context:\n" + "\n".join(sorted(set(relationships)))


# ---------------------------------------------------------------------------
# Retriever
# ---------------------------------------------------------------------------

class _GraphRetriever(BaseRetriever):
    graph: object
    entity_extractor: object
    depth: int = GRAPH_DEPTH
    k: int = TOP_K

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        context = _graph_retrieve(self.graph, self.entity_extractor, query, self.depth)
        return [Document(page_content=context)]


# ---------------------------------------------------------------------------
# Vector store
# ---------------------------------------------------------------------------

class GraphVectorStore(BaseVectorStore):
    tool_name = "graph_search_codebase"
    tool_description = "Search the codebase using a knowledge graph of code relationships. Best for understanding how classes, functions, and modules relate to each other."

    def __init__(
        self,
        relationship_extractor,
        entity_extractor,
        depth: int = GRAPH_DEPTH,
        embedding_model: str = EMBEDDING_MODEL,
        top_k: int = TOP_K,
    ):
        super().__init__(embedding_model=embedding_model, top_k=top_k)
        self.relationship_extractor = relationship_extractor
        self.entity_extractor = entity_extractor
        self.depth = depth
        self._retriever: _GraphRetriever = None

    def build(self, chunks: list[Document]) -> None:
        relationships = _extract_relationships(self.relationship_extractor, chunks)
        graph = _build_graph(relationships)
        self._retriever = _GraphRetriever(
            graph=graph,
            entity_extractor=self.entity_extractor,
            depth=self.depth,
            k=self.top_k,
        )

    def as_retriever(self, k: int = TOP_K) -> _GraphRetriever:
        self._retriever.k = k
        return self._retriever
