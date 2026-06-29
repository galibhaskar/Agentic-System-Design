import chromadb
from dotenv import load_dotenv
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from langchain_core.messages import HumanMessage, AIMessage

from my_claude.observability.logger import get_logger
from my_claude.config import config
from my_claude.llm.factory import get_llm, get_embedder
from my_claude.context.indexers.indexer_factory import get_indexer, show_semantic_index
from my_claude.agent.orchestrator import handle_query
from my_claude.memory.session_management import get_current_session, create_session, switch_session
from my_claude.memory.short_term import get_session_history

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
    session_id = get_current_session()
    console.print(f"[green]✓ Ready [/green]\n")
    return llm, embedder, index, session_id

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

    llm, embedder, index, session_id = initialize()

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
            response = handle_query(question, thread_id=session_id)
            console.print(f"\n\n[bold green]Assistant:[/bold green] {response}\n\n")
        elif user_input == "/show_semantic_index":
            logger.info("Showing semantic index")
            show_semantic_index()(index)
        elif user_input == "/show_session_history":
            logger.info(f"Showing session history for session ID: {session_id}")
            history = get_session_history(session_id)
            if not history:
                console.print("[yellow]No session history found.[/yellow]")
            else:
                console.print(f"[dim]Session History for ID: {session_id}[/dim]")
                for msg in history:
                    role = "[bold blue]User:[/bold blue]" if isinstance(msg, HumanMessage) else "[bold green]Assistant:[/bold green]"
                    console.print(f"{role} {msg.content}")
        elif user_input == "/new_session":
            session_id = create_session()
            logger.info(f"Created new session ID: {session_id}")
            console.print(f"[green]Created new session ID: {session_id}[/green]")
        elif user_input.startswith("/switch_session"):
            new_session_id = user_input.removeprefix("/switch_session ").strip()
            session_id = switch_session(new_session_id)
            logger.info(f"Switched to session ID: {session_id}")
            console.print(f"[yellow]Switched to session ID: {session_id}[/yellow]")
        elif user_input == "/current_session":
            console.print(f"[blue]Current session ID: {session_id}[/blue]")
        else:
           logger.warning(f"Unknown command received: {user_input}")
           console.print("[yellow]Unknown command. Try:[/yellow]")
           console.print("  [bold]/ask <question>[/bold]          — ask a question about the codebase")
           console.print("  [bold]/show_semantic_index[/bold]              — show all chunks in the index")
           console.print("  [bold]/show_session_history[/bold]              — show the history of the current session")
           console.print("  [bold]/new_session[/bold]             — start a fresh conversation")
           console.print("  [bold]/switch_session <session_id>[/bold]     — resume a past session")
           console.print("  [bold]/current_session[/bold]                 — show current session id")


if __name__ == "__main__":
    run()