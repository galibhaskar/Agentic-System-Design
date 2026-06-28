import chromadb
from dotenv import load_dotenv
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from my_claude.observability.logger import get_logger
from my_claude.config import config
from my_claude.llm.factory import get_llm, get_embedder
from my_claude.context.indexers.factory import get_indexer, show_semantic_index
from my_claude.agent.orchestrator import handle_query

load_dotenv()
console = Console()
logger = get_logger(__name__)

def initialize():
    """
    Initialize the llm, embedder and collection based on the configuration.
    """
    llm = get_llm()
    embedder = get_embedder()
    console.print(f"[dim]LLM: {config['llm']['provider']} / {config['llm']['model']}[/dim]")
    console.print(f"[dim]Embedder: {config['embedder']['provider']} / {config['embedder']['model']}[/dim]")

    index = _get_or_create_index()
    console.print(f"[green]✓ Ready [/green]\n")
    return llm, embedder, index

def _get_or_create_index():
    """
    Get or create the semantic index or qdrant index based on the configuration.
    """
    repo_path = str(Path.cwd())
    logger.info(f"Checking index for repo: {repo_path}")
    console.print(f"[dim]Checking index for repo: {repo_path}[/dim]")
    return get_indexer()(repo_path)

def run():
    """
    Main function to run the application.
    """
    logger.info("Starting the My Claude Application...")
    console.print("\n[bold green]Welcome to the My Claude Application - Code Assistant RAG![/bold green]\n")
    console.print("Type [bold red]'/exit'[/bold red] to quit the application.\n")

    llm, embedder, index = initialize()

    while True:
        user_input = Prompt.ask("[bold blue]>[/bold blue]")
        if user_input.lower() == "/exit":
            logger.info("Exiting the application.")
            console.print("[bold red]Exiting the application. Goodbye![/bold red]")
            break
        elif user_input.startswith("/ask"):
            question = user_input.removeprefix("/ask ").strip()
            logger.info(f"Ask command received: {question}")
            console.print(f"[dim]Searching for: {question}...[/dim]")
            response = handle_query(question)
            console.print(f"\n\n[bold green]Assistant:[/bold green] {response}\n\n")
        elif user_input == "/show_semantic_index":
            logger.info("Showing semantic index")
            show_semantic_index()(index)

        else:
            # invalid command handling
            logger.warning(f"Invalid command received: {user_input}")

if __name__ == "__main__":
    run()