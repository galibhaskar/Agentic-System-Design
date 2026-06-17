import ast
from langchain_core.documents import Document
from .base_chunker import BaseChunker, CHUNK_SIZE, CHUNK_OVERLAP, LANGUAGE


class ASTChunker(BaseChunker):
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP, language: str = LANGUAGE):
        super().__init__(chunk_size=chunk_size, chunk_overlap=chunk_overlap, language=language)

    def chunk(self, docs: list[Document]) -> list[Document]:
        chunks = []

        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            code = doc.page_content

            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                print(f"Error parsing {source}: {e}")
                chunks.append(doc)
                continue

            for node in ast.walk(tree):
                for child in ast.iter_child_nodes(node):
                    child.parent = node

            for node in ast.walk(tree):
                parent = getattr(node, "parent", None)

                if isinstance(node, ast.ClassDef) and isinstance(parent, ast.Module):
                    chunk_code = ast.get_source_segment(code, node)
                    if chunk_code:
                        chunks.append(Document(
                            page_content=chunk_code,
                            metadata={**doc.metadata, "type": "class", "name": node.name},
                        ))

                elif isinstance(node, ast.FunctionDef) and isinstance(parent, ast.Module):
                    chunk_code = ast.get_source_segment(code, node)
                    if chunk_code:
                        chunks.append(Document(
                            page_content=chunk_code,
                            metadata={**doc.metadata, "type": "function", "name": node.name},
                        ))

        return chunks
