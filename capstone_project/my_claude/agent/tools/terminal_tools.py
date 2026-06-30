import subprocess
import os
from langchain.tools import tool

_BLOCKED_COMMANDS = {"rm -rf /", "mkfs", "dd if=", ":(){:|:&};:"}
_TIMEOUT_SECONDS = 30

@tool
def run_command(command: str) -> str:
    """
    Executes a shell command and returns its output.

    Args:
        command (str): The shell command to execute.
    Returns:
        str: The output of the command or an error message if it fails or times out.
    """
    try:
        # Execute the command and capture the output
        result = subprocess.run(
            command, shell=True,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS
        )
        return _format_command_output(result)
    except subprocess.CalledProcessError as e:
        # Return the error message if the command fails
        return f"Error executing command: {e.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {_TIMEOUT_SECONDS} seconds"

@tool
def run_command_in_directory(command: str, directory: str) -> str:
    """
    Executes a shell command in a specified directory and returns its output.

    Args:
        command (str): The shell command to execute.
        directory (str): The directory in which to execute the command.
    Returns:
        str: The output of the command or an error message if it fails or times out.
    """
    if not os.path.isdir(directory):
        return f"Error: '{directory}' is not a valid directory."

    if any(blocked in command for blocked in _BLOCKED_COMMANDS):
        return "Error: Command contains blocked operations."

    try:
        # Execute the command in the specified directory and capture the output
        result = subprocess.run(
            command, shell=True,
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS
        )
        return _format_command_output(result)
    except subprocess.CalledProcessError as e:
        # Return the error message if the command fails
        return f"Error executing command: {e.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return f"Command timed out after {_TIMEOUT_SECONDS} seconds"

def _format_command_output(result: subprocess.CompletedProcess) -> str:
    """
    Formats the output of a subprocess command.

    Args:
        result (subprocess.CompletedProcess): The result of the executed command.
    Returns:
        str: Formatted output or error message.
    """
    parts = []

    if result.stdout:
        parts.append(f"Output:\n{result.stdout.strip()}")
    if result.stderr:
        parts.append(f"Error:\n{result.stderr.strip()}")
    if result.returncode != 0:
        parts.append(f"Exit Code: {result.returncode}")
    return "\n".join(parts) if parts else "No output or error." 