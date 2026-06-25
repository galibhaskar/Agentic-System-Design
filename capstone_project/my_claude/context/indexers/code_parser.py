from pathlib import Path
from dataclasses import dataclass
from tree_sitter_language_pack import get_parser
from my_claude.observability.logger import get_logger

logger = get_logger(__name__)

EXTENSION_TO_LANGUAGE = {
  ".py": "python",
  ".js": "javascript",
  ".jsx": "javascript",
  ".ts": "typescript",
  ".tsx": "tsx",
  ".java": "java",
  ".go": "go",
  ".rs": "rust",
  ".cpp": "cpp",
  ".c": "c",
  ".cs": "c_sharp",
  ".rb": "ruby",
  ".php": "php",
  ".swift": "swift",
  ".kt": "kotlin",
  ".sh": "bash",
}

# Text/config files have no meaningful AST — we chunk them by line count instead.
TEXT_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json", ".toml"}
ALL_EXTENSIONS = set(EXTENSION_TO_LANGUAGE.keys()) | TEXT_EXTENSIONS

# Sliding window settings for text files and AST fallback.
# CHUNK_OVERLAP ensures context isn't lost at chunk boundaries.
CHUNK_SIZE = 50
CHUNK_OVERLAP = 10

# Tree-sitter node type names that correspond to a named, indexable block.
# These are consistent across languages — tree-sitter uses the same names where possible.
BLOCK_NODE_TYPES = {
  "function_definition", "function_declaration", "method_definition",
  "arrow_function", "class_definition", "class_declaration",
  "method_declaration", "constructor_declaration", "interface_declaration",
  "function_item",    # Rust uses this instead of function_definition
  "func_declaration", # Go
}

@dataclass
class ParsedChunk:
  name: str
  type: str        # "function" | "class" | "block"
  content: str
  source: str      # absolute path to the file
  start_line: int
  end_line: int

def parse_file(filepath: str) -> list[ParsedChunk]:
    """
    Entry point - routes to AST parsing or sliding window based on file_type

    Args:
        filepath (str): Path to the source code file.
    """
    extension = Path(filepath).suffix.lower()

    if extension in TEXT_EXTENSIONS:
        lines = Path(filepath).read_text(encoding="utf-8").splitlines()
        return _sliding_window_chunking(lines, filepath)

    language_name = EXTENSION_TO_LANGUAGE.get(extension)

    if not language_name:
        logger.warning(f"Unsupported file extension '{extension}' for file '{filepath}'. Skipping.")
        return []
    
    source = Path(filepath).read_text(encoding="utf-8", errors="ignore")

    return _parse_with_treesitter(source, filepath, language_name)

def _sliding_window_chunking(lines: list[str], filepath: str) -> list[ParsedChunk]:
    """
    Chunk text files using a sliding window approach.

    Args:
        lines (list[str]): List of lines from the text file.
        filepath (str): Absolute path to the source file.
    """
    chunks = []
    total_lines = len(lines)
    start = 0
    step = CHUNK_SIZE - CHUNK_OVERLAP

    for i, start in enumerate(range(0, total_lines, step)):
        end = min(start + CHUNK_SIZE, total_lines)
        chunk_content = "\n".join(lines[start:end])
        if chunk_content.strip():  # Only add non-empty chunks
            chunk_name = f"{Path(filepath).name}_chunk_{i+1}"
            chunks.append(ParsedChunk(
                name=chunk_name,
                type="block",
                content=chunk_content,
                source=filepath,
                start_line=start + 1,
                end_line=end
            ))
        if end == total_lines:
            break # Stop if we've reached the end of the file

    logger.info(f"Sliding window chunking produced {len(chunks)} chunks for file '{filepath}'.")
    return chunks

def _parse_with_treesitter(source: str, filepath: str, language_name: str) -> list[ParsedChunk]:
  """Parse source with the appropriate tree-sitter grammar and extract named blocks."""
  logger.info(f"Parsing {language_name} file: {filepath}")
  parser = get_parser(language_name)
  tree = parser.parse(source)
  lines = source.splitlines()


  chunks = []
  _walk(_root_node(tree), source, filepath, chunks, depth=0)


  # If the AST yielded nothing (e.g. a file with only imports), fall back to line chunks
  if not chunks:
      logger.warning(f"No AST blocks found in {filepath}, falling back to sliding window")
      return _sliding_window(lines, filepath)


  logger.info(f"Parsed {len(chunks)} chunks from {filepath}")
  return chunks


def _walk(node, source: str, filepath: str, chunks: list, depth: int):
  """
  Recursively walk the AST. When a named block node is found, record it and stop
  descending — this keeps chunks at the top level and avoids duplicating nested functions.
  """
  node_type = _node_type(node)
  if node_type in BLOCK_NODE_TYPES:
      name = _extract_name(node, source)
      content = _node_text(node, source)
      chunk_type = "class" if "class" in node_type else "function"
      start_line = _start_line(node)
      end_line = _end_line(node)
      chunks.append(ParsedChunk(
          name=name,
          type=chunk_type,
          content=content,
          source=filepath,
          start_line=start_line,
          end_line=end_line,
      ))
      logger.debug(f"  Found {chunk_type} '{name}' (lines {start_line}-{end_line})")
      return  # stop here — don't index nested functions/classes as separate chunks


  for child in _children(node):
      _walk(child, source, filepath, chunks, depth + 1)


def _extract_name(node, source: str) -> str:
  """Find the identifier child of a block node and return its text as the chunk name."""
  for child in _children(node):
      if _node_type(child) in ("identifier", "name", "property_identifier"):
          return _node_text(child, source)
  return _node_type(node)  # fallback to node type if no name found


def _root_node(tree):
  root = tree.root_node
  return root() if callable(root) else root


def _node_type(node) -> str:
  node_type = getattr(node, "type", None)
  if node_type is not None:
      return node_type
  return node.kind()


def _children(node):
  children = getattr(node, "children", None)
  if children is not None:
      return children
  return [node.child(index) for index in range(node.child_count())]


def _start_byte(node) -> int:
  value = node.start_byte
  return value() if callable(value) else value


def _end_byte(node) -> int:
  value = node.end_byte
  return value() if callable(value) else value


def _node_text(node, source: str) -> str:
  return source.encode("utf-8")[_start_byte(node):_end_byte(node)].decode("utf-8", errors="ignore")


def _start_line(node) -> int:
  point = getattr(node, "start_point", None)
  if point is not None:
      return point[0] + 1
  return node.start_position().row + 1


def _end_line(node) -> int:
  point = getattr(node, "end_point", None)
  if point is not None:
      return point[0] + 1
  return node.end_position().row + 1

def get_source_files(repo_path: str, skip_dirs: list[str] = None) -> list[str]:
  """Recursively find all indexable source files under repo_path, skipping build/env dirs."""
  skip = set(skip_dirs or [".venv", "venv", "__pycache__", ".git", "node_modules", "dist", "build"])
  files = [
      str(path) for path in Path(repo_path).rglob("*")
      if path.suffix.lower() in ALL_EXTENSIONS
      and not any(part in skip for part in path.parts)
  ]
  logger.info(f"Found {len(files)} source files in {repo_path}")
  return files
