import os
import uuid
import click
from rich.console import Console,Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn

from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.store.base import BaseStore

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
import os
import re
import time
import uuid
import traceback
import subprocess
import threading
from typing import List
import json

# from langfuse.langchain import CallbackHandler
# from langfuse import Langfuse

from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
from rich.table import Table
from rich.live import Live


from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.store.memory import InMemoryStore
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langgraph.store.base import BaseStore
from langgraph.types import Command, interrupt


from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from dotenv import load_dotenv
from loguru import logger


from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type


from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings

from e2b_code_interpreter import Sandbox

try:
    from google.api_core import exceptions as google_exceptions
except ImportError:
    class google_exceptions:
        InternalServerError = type("InternalServerError", (Exception,), {})
        ServiceUnavailable = type("ServiceUnavailable", (Exception,), {})
        DeadlineExceeded = type("DeadlineExceeded", (Exception,), {})
        ResourceExhausted = type("ResourceExhausted", (Exception,), {})
        Aborted = type("Aborted", (Exception,), {})

load_dotenv()
# Add this class definition after your imports

# Define the specific exceptions to retry on (500s, 503s, timeouts, rate limits)
RETRYABLE_EXCEPTIONS = (
    google_exceptions.InternalServerError,   # 500 - Internal Server Error
    google_exceptions.ServiceUnavailable,    # 503 - Service Unavailable
    google_exceptions.DeadlineExceeded,      # 504 / Client-side Timeout
    google_exceptions.ResourceExhausted,     # 429 - Rate Limiting
    google_exceptions.Aborted,               # Other transient connection errors
)

class RetryingChatGoogleGenerativeAI(ChatGoogleGenerativeAI):
    """
    A ChatGoogleGenerativeAI subclass that automatically retries API calls
    on specific, transient errors using an exponential backoff strategy.
    """
    @retry(
        # Wait with exponential backoff, starting at 2s, up to 60s between retries.
        wait=wait_exponential(multiplier=1, min=2, max=60),
        # Retry up to 5 times before giving up.
        stop=stop_after_attempt(5),
        # Only retry on the specified Google API exceptions.
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        # If all retries fail, re-raise the last exception.
        reraise=True
    )
    def invoke(self, *args, **kwargs):
        return super().invoke(*args, **kwargs)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        reraise=True
    )
    async def ainvoke(self, *args, **kwargs):
        return await super().ainvoke(*args, **kwargs)

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(5),
        retry=retry_if_exception_type(RETRYABLE_EXCEPTIONS),
        reraise=True
    )
    def stream(self, *args, **kwargs):
        yield from super().stream(*args, **kwargs)

logger.add(
    lambda msg: print(msg, end=""),
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <green>{message}</green>"
    if "INFO" in "{level}"
    else "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
)
model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cpu"}
encode_kwargs = {"normalize_embeddings": False}
hf = HuggingFaceEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

gemini_2_flash = None

def setup_api_keys():
    """
    Handles the setup for both Gemini and E2B API keys. Checks environment
    variables first, then prompts the user if a key is missing.
    """
    # --- Handle Google Gemini API Key ---
    if not os.getenv("GOOGLE_API_KEY"):
        console.print(
            Panel.fit(
                "[bold]🔑 Google Gemini API Key Required[/bold]\n\n"
                "BlitzCoder uses Google's Gemini model. Please provide your API key.",
                border_style="cyan"
            )
        )
        google_api_key = Prompt.ask(
            "🔑 [bold green]Paste your Gemini API key[/bold green]", password=True
        )
        if not validate_google_api_key(google_api_key):
            show_error("Invalid Gemini API key. Please restart and try again.")
            exit(1)
        os.environ["GOOGLE_API_KEY"] = google_api_key
        show_success("Gemini API key validated and set for this session.")
    else:
        show_success("Gemini API key found in environment variables.")

    # Initialize the model now that we're sure the key is set
    try:
        initialize_gemini_2_flash()
    except Exception as e:
        show_error(f"Failed to initialize Gemini model: {e}")
        exit(1)

    # --- Handle E2B Sandbox API Key ---
    if not os.getenv("E2B_API_KEY"):
        explanation_panel = Panel.fit(
            """
[bold]Why a Sandbox is Critical (Preventing Command Injection)[/bold]

When an AI agent generates shell commands, there's a risk of 'command injection'. A malicious or flawed command could potentially delete important files or read sensitive data from your computer.

BlitzCoder prevents this by executing **all** shell commands inside the [bold]E2B secure sandbox[/bold], which is an isolated, temporary cloud environment with no access to your local files.

To enable this critical security feature, you need a free API key from E2B.

[bold]How to get your key:[/bold]
1. Go to [blue u]https://e2b.dev[/blue u] and sign up.
2. Copy your free API key and paste it below.
            """,
            title="[bold yellow]🔒 Action Required: Secure Sandbox Setup[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        console.print(explanation_panel)
        e2b_api_key = Prompt.ask(
            "🔑 [bold green]Paste your E2B API key[/bold green]", password=True
        )
        if not e2b_api_key or not e2b_api_key.strip():
            show_error("E2B API key cannot be empty. Exiting.")
            exit(1)
        os.environ["E2B_API_KEY"] = e2b_api_key
        show_success("E2B Sandbox API key set for this session.")
    else:
        show_success("E2B Sandbox API key found in environment variables.")

def initialize_gemini_2_flash(api_key: str = None):
    """Initialize the Gemini 2.0 Flash model with the provided API key"""
    global gemini_2_flash
    if api_key:
        api_key_to_use = api_key
    else:
        api_key_to_use = os.getenv("GOOGLE_API_KEY")

    if not api_key_to_use:
        raise ValueError(
            "GOOGLE_API_KEY is required to initialize Gemini 2.0 Flash model"
        )

    gemini_2_flash =RetryingChatGoogleGenerativeAI(
        model="gemini-2.5-flash", api_key=api_key_to_use, max_tokens=100000
    )
    return gemini_2_flash


def get_gemini_25_flash():
    """Get the initialized Gemini 2.5 Flash model"""
    global gemini_2_flash
    if gemini_2_flash is None:
        initialize_gemini_2_flash()
    return gemini_2_flash


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

console = Console()

def print_welcome_banner():
    """Prints an enhanced welcome banner with instructions and capabilities."""
    banner_text = Text(
        """
      ██████╗ ██╗     ██╗████████╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗██████╗ 
      ██╔══██╗██║     ██║╚══██╔══╝╚══███╔╝██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
      ██████╔╝██║     ██║   ██║     ███╔╝ ██║     ██║   ██║██║  ██║█████╗  ██████╔╝
      ██╔══██╗██║     ██║   ██║    ███╔╝  ██║     ██║   ██║██║  ██║██╔══╝  ██╔══██╗
      ██████╔╝███████╗██║   ██║   ███████╗╚██████╗╚██████╔╝██████╔╝███████╗██║  ██║
      ╚═════╝ ╚══════╝╚═╝   ╚═╝   ╚══════╝ ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
      """,
        style="orange1",
        justify="center",
    )

    welcome_message = Markdown("""
### Welcome to BlitzCoder! Your AI-Powered Development Assistant.
This tool leverages AI to help you with a wide range of development tasks, right from your terminal.

---
### Key Capabilities:
*   **Project Scaffolding:** Generate entire, production-ready project structures for any framework.
*   **Code Generation & Refactoring:** Write, explain, and refactor code in any language.
*   **Secure Command Execution:** Run shell commands, linters (`ruff`), and installers (`pip`) in a secure, isolated sandbox.
*   **Debugging Assistance:** Run servers (FastAPI, Node.js), capture logs, and get AI-powered suggestions for errors.
*   **Filesystem Operations:** Navigate your codebase, inspect files, and manage your project directory.
*   **Semantic Memory:** Remembers the context of your conversation for more relevant assistance over time.

---
### How to Use:
Simply type your request in plain English. Here are some examples:
- `scaffold a new go project for a REST API with Fiber`
- `run the ruff formatter on my current directory`
- `explain the code in src/main.py`
- `search: what was the database model we discussed earlier?`
""")
    
    panel_content = Group(banner_text, welcome_message)

    panel = Panel(
        panel_content,
        title="[bold orange1]⚡ BLITZCODER CLI[/bold orange1]",
        subtitle="[orange1]AI-Powered Dev Assistant[/orange1]",
        border_style="orange1",
        width=140,
        expand=True,
        padding=(2, 2),
    )
    console.print(panel)


def show_success(msg):
    console.print(Panel(f"[green]✅ {msg}", title="Success", style="green"))


def show_error(msg):
    console.print(Panel(f"[red]❌ {msg}", title="Error", style="red"))


def show_info(msg):
    console.print(f"[cyan]{msg}[/cyan]")


def print_agent_response(text: str, title: str = "BlitzCoder"):
    """Display agent output inside a Rich panel box with orange color"""
    console.print(
        Panel.fit(
            Markdown(text),
            title=f"[bold orange1]{title}[/bold orange1]",
            border_style="orange1",
        )
    )


def show_code(code: str, lang: str = "python"):
    syntax = Syntax(code, lang, theme="monokai", line_numbers=True)
    console.print(syntax)


def build_rich_tree(root_path: str) -> Tree:
    root_name = os.path.basename(os.path.abspath(root_path))
    tree = Tree(f"📁 [bold blue]{root_name}[/bold blue]")

    def add_nodes(directory: str, branch: Tree):
        try:
            for entry in sorted(os.listdir(directory)):
                full_path = os.path.join(directory, entry)
                if os.path.isdir(full_path):
                    sub_branch = branch.add(f"📁 [bold]{entry}[/bold]")
                    add_nodes(full_path, sub_branch)
                else:
                    branch.add(f"📄 {entry}")
        except PermissionError:
            branch.add("[red]Permission Denied[/red]")

    add_nodes(root_path, tree)
    return tree


def simulate_progress(task_desc: str):
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(f"[green]{task_desc}", total=100)
        while not progress.finished:
            progress.update(task, advance=5)
            time.sleep(0.05)


class PersistentPowerShell:
    def _init_(self):
        self.process = subprocess.Popen(
            ["powershell.exe", "-NoLogo", "-NoExit", "-Command", "-"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
        self.lock = threading.Lock()

    def run_command(self, command, timeout=30):
        with self.lock:
            # Write the command and a marker to know when output ends
            marker = "END_OF_COMMAND"
            self.process.stdin.write(command + f"\nWrite-Output '{marker}'\n")
            self.process.stdin.flush()

            output_lines = []
            for line in self.process.stdout:
                if marker in line:
                    break
                output_lines.append(line)
            return "".join(output_lines)

    def close(self):
        with self.lock:
            self.process.stdin.write("exit\n")
            self.process.stdin.flush()
            self.process.terminate()
            self.process.wait()


ps = PersistentPowerShell()

tree_pattern = r"(?:\w+)?\n(.*?)"
python_pattern = r"(?:python)?\\n(.*?)"
code_pattern = r"(?:\w+)?\n(.*?)\n"



class AgentState(MessagesState):
    documents: list[str]

model_name = "sentence-transformers/all-mpnet-base-v2"
model_kwargs = {"device": "cpu"}
semantic_memory_store = InMemoryStore(
    index={
        "embed": HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        ),
        "dims": 768,  # Google embedding dimension
        "fields": ["memory", "$"],  # Fields to embed
    }
)

error_logs_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Hey take a look at the error logs: {error_logs} and tell me how can I resolve them",
        ),
        ("user", "{error_logs}"),
    ]
)


def send_error_logs_to_agent(error_logs):
    """
    Send error logs to the Gemini model for analysis and suggestions.

    Args:
        error_logs (list): A list of error log lines (strings) to send to the agent.

    Returns:
        None
    """
    if not error_logs:
        show_info("No error logs to send to the agent.")
        return
    logs_text = "".join(error_logs)
    prompt = error_logs_prompt.format(error_logs=logs_text)
    show_info("\n--- Sending error logs to Gemini ---")
    response = get_gemini_2_flash().invoke(prompt)
    show_info("\n--- Gemini Response ---")
    show_info(response.content)


@tool
def windows_powershell_command(command: str) -> str:
    """
    Run a command in a windows PowerShell session and return the output.
    The session preserves state (variables, working directory, etc.) between calls.
    Args :
     command (str) : Windows Command to execute
    Return :
     Output (str) : Output after executing the command
    """
    return ps.run_command(command)


@tool
def inspect_a_file(path: str):
    """
    Reads and returns the content of the file at the given path as a string.
    Handles file not found and decoding errors gracefully.

    Args:
        path (str): The path to the file to inspect.

    Returns:
        str: The content of the file, or an error message if the file cannot be read.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except UnicodeDecodeError:
        return f"Error: Could not decode file (not UTF-8): {path}"
    except Exception as e:
        return f"Error reading file {path}: {e}"


@tool
def execute_python_code(path: str):
    """
    Args (str): Path of the python file to be executed
    Returns (str): Output and errors of the python file execution, logged and returned as a string
    """
    try:
        show_info(f"Executing Python file: {path}")
        process = subprocess.Popen(
            ["python", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
        logs = []

        def read_logs():
            for line in process.stdout:
                if "ERROR" in line or "Traceback" in line:
                    show_error(line.rstrip())
                elif "CRITICAL" in line:
                    show_error(line.rstrip())
                elif "WARNING" in line:
                    show_info(line.rstrip())
                elif "DEBUG" in line:
                    show_info(line.rstrip())
                else:
                    show_info(line.rstrip())
                logs.append(line)

        t = threading.Thread(target=read_logs)
        t.start()
        t.join(timeout=30)  # Wait for logs or timeout
        process.terminate()
        process.wait()
        show_info(f"Execution of {path} completed.")
        return "".join(logs)
    except Exception as e:
        show_error(f"Exception occurred while executing {path}: {e}")
        return f"Exception occurred while executing {path}: {e}"


@tool
def write_code_to_file(path: str, code: str):
    """
    Write the provided code string to the specified file path, creating parent directories if needed.
    If the code contains class or function definitions, append an if _name_ == "_main_": block to run the function(s) or instantiate the class and invoke its methods.

    Args:
        path (str): The file path to write to.
        code (str): The code/content to write into the file.

    Returns:
        str: A message indicating success or any error encountered.
    """
    import re

    try:
        # Detect top-level classes and functions
        class_names = re.findall(r"^class\s+(\w+)\s*\(", code, re.MULTILINE)
        func_names = re.findall(r"^def\s+(\w+)\s*\(", code, re.MULTILINE)
        main_block = ""
        if class_names or func_names:
            main_block += '\n\nif _name_ == "_main_":\n'
            for cname in class_names:
                main_block += f"    obj = {cname}()\n"
                # Try to find methods (excluding _init_)
                method_matches = re.findall(
                    rf"^\s+def\s+(\w+)\s*\(", code, re.MULTILINE
                )
                for m in method_matches:
                    if m != "_init_":
                        main_block += f"    obj.{m}()\n"
            for fname in func_names:
                main_block += f"    {fname}()\n"
        # Append main block if needed
        final_code = code.rstrip() + main_block
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(final_code)
        show_info(f"Wrote code to file: {os.path.relpath(path, PROJECT_ROOT)}")
        return f"Successfully wrote code to {os.path.relpath(path, PROJECT_ROOT)} \n"
    except Exception as e:
        show_error(f"Error writing code to {os.path.relpath(path, PROJECT_ROOT)}: {e}")
        return f"Error writing code to {os.path.relpath(path, PROJECT_ROOT)}: {e}"


@tool
def refactoring_code(refactored_code: str, error_file_path: str):
    """
    Overwrite the specified file with the provided refactored code.

    Args:
        refactored_code (str): The new code to write into the file.
        error_file_path (str): The path to the file to be overwritten.

    Returns:
        str: A success message if the file was written, or an error message if writing failed.
    """
    try:
        show_info(f"Writing refactored code to {error_file_path}")
        with open(error_file_path, "w", encoding="utf-8") as file:
            file.write(refactored_code)
        show_info(f"Successfully wrote refactored code to {error_file_path}")
        return f"Successfully wrote refactored code to {error_file_path}"
    except Exception as e:
        show_error(f"Error writing to {error_file_path}: {e}")
        return f"Error writing to {error_file_path}: {e}"


@tool
def extract_content_within_a_file(path: str):
    """
    Extract and return the content of a file at the specified path.

    Args:
        path (str): The path to the file whose content should be extracted.

    Returns:
        str: The content of the file as a string, or an error message if the file cannot be read.
    """
    try:
        show_info(
            f"Extracting content from file: {os.path.relpath(path, PROJECT_ROOT)}"
        )
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        show_info(
            f"Successfully extracted content from {os.path.relpath(path, PROJECT_ROOT)}"
        )
        return content
    except FileNotFoundError:
        show_error(f"File not found: {os.path.relpath(path, PROJECT_ROOT)}")
        return f"Error: File not found: {os.path.relpath(path, PROJECT_ROOT)}"
    except UnicodeDecodeError:
        show_error(
            f"Could not decode file (not UTF-8): {os.path.relpath(path, PROJECT_ROOT)}"
        )
        return f"Error: Could not decode file (not UTF-8): {os.path.relpath(path, PROJECT_ROOT)}"
    except Exception as e:
        show_error(f"Error reading file {os.path.relpath(path, PROJECT_ROOT)}: {e}")
        return f"Error reading file {os.path.relpath(path, PROJECT_ROOT)}: {e}"


@tool
def navigate_entire_codebase_given_path(path: str):
    """
    Recursively navigate and render all files and directories in the given path using a rich Tree view,
    skipping cache and hidden files/folders.

    Args:
        path (str): The root directory path from which to start navigation.

    Returns:
        None: Directly prints the rich Tree view to the console.
    """
    skip_dirs = {"_pycache_", ".git", ".venv", ".cache", "node_modules"}
    skip_files = {".DS_Store"}
    skip_exts = {".pyc", ".pyo"}
    file_list = []
    console = Console()
    base_name = os.path.basename(os.path.abspath(path)) or path
    tree = Tree(f"📁 [bold blue]{base_name}[/bold blue]")

    def add_nodes(current_path: str, branch: Tree):
        try:
            entries = sorted(os.listdir(current_path))
            for entry in entries:
                full_path = os.path.join(current_path, entry)
                if os.path.isdir(full_path):
                    if entry in skip_dirs or entry.startswith("."):
                        continue
                    sub_branch = branch.add(f"📁 [bold]{entry}[/bold]")
                    add_nodes(full_path, sub_branch)
                else:
                    if (
                        entry in skip_files
                        or entry.startswith(".")
                        or any(entry.endswith(ext) for ext in skip_exts)
                    ):
                        continue
                    icon = "🐍" if entry.endswith(".py") else "📄"
                    branch.add(f"{icon} [green]{entry}[/green]")
        except Exception as e:
            branch.add(f"[red]Error reading {current_path}: {e}[/red]")

    add_nodes(path, tree)
    console.print(tree)
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith(".")]
        for name in dirs:
            if name not in skip_dirs and not name.startswith("."):
                file_list.append(os.path.relpath(os.path.join(root, name), path))
        for name in files:
            if (
                name not in skip_files
                and not name.startswith(".")
                and not any(name.endswith(ext) for ext in skip_exts)
            ):
                file_list.append(os.path.relpath(os.path.join(root, name), path))
    return file_list


# 2. Tool definition
@tool
def run_uvicorn_and_capture_logs(
    app_path="main:app", host="127.0.0.1", port=8000, reload=True, max_lines=100
):
    """
    Run a Uvicorn server for a FastAPI app and capture its logs.

    Args:
        app_path (str): The import path to the FastAPI app (e.g., 'main:app').
        host (str): Host address to bind the server to.
        port (int): Port number to bind the server to.
        reload (bool): Whether to enable auto-reload for code changes.
        max_lines (int): Maximum number of log lines to capture before terminating.

    Returns:
        list: A list of log lines (strings) captured from the server output.
    """
    uvicorn_cmd = ["uvicorn", app_path, "--host", host, "--port", str(port)]
    if reload:
        uvicorn_cmd.append("--reload")

    show_info(f"Running command: {' '.join(uvicorn_cmd)}")
    process = subprocess.Popen(
        uvicorn_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )

    logs = []

    def read_logs():
        for line in process.stdout:
            if "ERROR" in line or "Traceback" in line:
                show_error(line.rstrip())
            elif "CRITICAL" in line:
                show_error(line.rstrip())
            elif "WARNING" in line:
                show_info(line.rstrip())
            elif "DEBUG" in line:
                show_info(line.rstrip())
            else:
                show_info(line.rstrip())
            logs.append(line)
            if len(logs) >= max_lines:
                show_info("Max log lines reached, terminating process.")
                process.terminate()
                break

    t = threading.Thread(target=read_logs)
    t.start()
    t.join(timeout=15)  # Wait for logs or timeout

    process.terminate()
    process.wait()
    show_info("Uvicorn process terminated.")
    return logs

@tool
def run_shell_command_in_sandbox(
    command: str, cwd: str = "/", timeout: int = 60
) -> str:
    """
    Executes a shell command (like ls, git, ruff, find, curl, etc even more) in a secure, isolated sandbox.
    This is the ONLY safe way to run general-purpose shell commands.
    The sandbox is ephemeral, has a full filesystem, and common command-line tools installed.

    Args:
        command (str): The shell command to execute.
        cwd (str): The working directory in the sandbox where the command should be run. Defaults to '/'.
        timeout (int): The maximum time in seconds to wait for the command to complete.

    Returns:
        str: A JSON string containing the command's 'stdout', 'stderr', and 'exit_code'.
    """
    show_info(f"Executing shell command in E2B sandbox: '{command}'")
    try:
        # The tool now simply assumes the API key is set in the environment.
        e2b_api_key = os.getenv("E2B_API_KEY")
        if not e2b_api_key:
            error_msg = "CRITICAL ERROR: E2B_API_KEY environment variable not found. The tool cannot run."
            show_error(error_msg)
            return json.dumps({"error": error_msg, "exit_code": -1})

        with Sandbox(api_key=e2b_api_key) as sandbox:
            exec_result = sandbox.commands.run(command, cwd=cwd, timeout=timeout)

            output = {
                "stdout": exec_result.stdout,
                "stderr": exec_result.stderr,
                "exit_code": exec_result.exit_code,
            }

            if exec_result.exit_code != 0:
                show_error(
                    f"Sandbox shell command failed with exit code {exec_result.exit_code}."
                )
                if exec_result.stderr:
                    console.print(
                        Panel(
                            exec_result.stderr,
                            title="[bold red]Stderr[/bold red]",
                            border_style="red",
                        )
                    )
            else:
                show_success("Sandbox shell command executed successfully.")

            return json.dumps(output, indent=2)

    except Exception as e:
        error_msg = f"An infrastructure error occurred while trying to run the shell command in the sandbox: {e}"
        show_error(error_msg)
        traceback.print_exc()
        if "Authentication failed" in str(e):
             show_error("Authentication with E2B failed. Please check your API key.")
        return json.dumps({"error": error_msg, "exit_code": -1})

@tool
def look_for_directory(path: str):
    """
    List all directories within the given path.

    LLM: If the user asks to list or look for directories in a path, invoke this tool directly and return the real output. Do NOT ask for permission or simulate output.

    Args:
        path (str): The root directory path to search for subdirectories.

    Returns:
        list: A list of directory names (relative to the given path) found within the path.
    """
    import os

    try:
        dirs = [
            name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))
        ]
        return dirs
    except Exception as e:
        return f"Error: {e}"


@tool
def run_node_js_server(cmd=str, cwd=str, max_lines=100):
    """
    Run a Node.js server command (e.g., with bun or npm) in a subprocess, capture its logs, and send them to the agent.

    Args:
        cmd (str): The command to run the Node.js server.
        cwd (str): The working directory for the command.
        max_lines (int): Maximum number of log lines to capture before terminating.

    Returns:
        list: A list of log lines (strings) captured from the server output.
    """
    node_cmd = cmd
    show_info(f"Running command: {node_cmd} in {cwd}")
    process = subprocess.Popen(
        node_cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1,
    )

    logs = []

    def read_logs():
        for line in process.stdout:
            if "ERROR" in line or "Traceback" in line:
                show_error(line.rstrip())
            elif "CRITICAL" in line:
                show_error(line.rstrip())
            elif "WARNING" in line:
                show_info(line.rstrip())
            elif "DEBUG" in line:
                show_info(line.rstrip())
            else:
                show_info(line.rstrip())
            logs.append(line)
            if len(logs) >= max_lines:
                show_info("Max log lines reached, terminating process.")
                process.terminate()
                break

    t = threading.Thread(target=read_logs)
    t.start()
    t.join(timeout=15)  # Wait for logs or timeout

    process.terminate()
    process.wait()

    show_info("\n--- Sending ALL output logs to CodeAgent ---")
    send_error_logs_to_agent(logs)

    error_logs = [line for line in logs if "ERROR" in line or "Traceback" in line]
    if error_logs:
        show_info("\n--- Sending only ERROR logs to CodeAgent ---")
        send_error_logs_to_agent(error_logs)
    else:
        show_info("\nNo error logs found in output.")

    return logs


@tool
def current_directory():
    """
    Get the current working directory path.

    Returns:
        str: The current working directory path.
    """
    show_info(f"Current directory: {os.getcwd()}")
    return os.getcwd()


@tool
def change_directory(path):
    """
    Change the current working directory to the specified path.

    Args:
        path (str): The target directory path to change to.

    Returns:
        str: The new current working directory after the change.
    """
    try:
        os.chdir(path)
        show_info(f"Changed directory to: {os.getcwd()}")
        return os.getcwd()
    except Exception as e:
        show_error(f"Failed to change directory to {path}: {e}")
        return f"Error: {e}"


@tool
def error_detection(error: str, path: str):
    """
    Accepts an error message/traceback as a string, logs it, and returns a formatted response.
    Args:
        error (str): The error message or traceback as a string.
        path (str): The path to the file where the error occurred.
    Returns:
        str: The logged error and a message for further action.
    """
    show_error(f"Error detected in {path}: {error}")
    # You can add more logic here to parse the error string and act accordingly
    return f"Error detected in {path}:\n{error}"


def validate_project_structure(tree_structure: str) -> bool:
    """
    Validate that the generated project structure is not overly complex.
    Returns True if the structure is acceptable, False if it's too complex.
    """
    lines = tree_structure.strip().split("\n")
    file_count = 0
    max_depth = 0

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Count files (lines that don't end with /)
        if (
            not line.endswith("/")
            and not line.endswith("│")
            and not line.endswith("├──")
            and not line.endswith("└──")
        ):
            file_count += 1

        # Calculate depth by counting leading spaces or tree characters
        depth = 0
        for char in line:
            if char in [" ", "│", "├", "└", "─"]:
                depth += 1
            else:
                break
        max_depth = max(max_depth, depth // 4)  # Approximate depth level

    # Reject if too many files or too deep
    if file_count > 25:
        show_error(f"❌ Project structure too complex: {file_count} files (max 25)")
        return False

    if max_depth > 5:
        show_error(f"❌ Project structure too deep: {max_depth} levels (max 5)")
        return False

    return True


@tool
def generate_project_structure(framework: str, use_case: str) -> str:
    """
    Generate a realistic, production-ready project folder structure for the given framework and use case.
    Returns the folder tree as a string.
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a backend architecture expert. Generate a SIMPLE and PRACTICAL project folder structure.

CRITICAL CONSTRAINTS - YOU MUST FOLLOW THESE:
- MAXIMUM 15-20 files total (including config files)
- NO duplicate directories or files
- NO overly complex nested structures (max 3-4 levels deep)
- Focus ONLY on core functionality
- Include only ESSENTIAL files for a working application
- NO enterprise-level complexity
- NO microservices architecture
- NO advanced features like monitoring, analytics, etc.
- Keep it SIMPLE and WORKING

Requirements:
- Follow {framework} conventions and file extensions
- Wrap output in triple backticks
- NO explanations, just the folder structure
- Small-to-medium scale application
- Basic CRUD operations only

Framework: {framework}
Use Case: {use_case}

Remember: SIMPLE, PRACTICAL, WORKING - NOT COMPLEX!""",
            ),
            (
                "user",
                "Generate a simple, practical folder structure for {framework} framework for {use_case}",
            ),
        ]
    )

    # Try up to 3 times to get a simple structure
    for attempt in range(3):
        messages = prompt_template.format_messages(
            framework=framework, use_case=use_case
        )
        result = get_gemini_2_flash().invoke(messages)
        match = re.search(tree_pattern, result.content, re.DOTALL)
        tree_structure = match.group(1).strip() if match else result.content

        # Validate the structure
        if validate_project_structure(tree_structure):
            show_info(f"✅ Generated simple project structure (attempt {attempt + 1})")
            return tree_structure
        else:
            show_info(f"⚠️ Structure too complex, retrying... (attempt {attempt + 1}/3)")

    # If all attempts failed, return a simple fallback structure
    show_error("❌ Failed to generate simple structure, using fallback")
    fallback_structure = f"""
{framework.lower()}-app/
├── src/
│   ├── main.{framework.lower()}
│   ├── config.py
│   ├── models.py
│   ├── routes.py
│   └── utils.py
├── tests/
│   └── test_main.py
├── requirements.txt
├── README.md
└── .gitignore
"""
    return fallback_structure.strip()


@tool
def generate_architecture_plan(
    framework: str, use_case: str, tree_structure: str
) -> str:
    """
    Generate a comprehensive architecture plan for the given project structure.
    Returns the plan as a JSON string.
    """
    reasoning_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert software architect with deep reasoning capabilities.

Analyze the given project structure and create a comprehensive architecture plan.

Your task:
1. ANALYZE the folder structure deeply
2. UNDERSTAND the relationships between components
3. PLAN the data flow and dependencies
4. IDENTIFY ALL files that need implementation
5. DETERMINE the content strategy for EACH file

Framework: {framework}
Use Case: {use_case}
Project Structure:
{tree_structure}

CRITICAL REQUIREMENTS:
- Every file in the project structure MUST be included in file_analysis
- Every file MUST have an implementation_priority (high, medium, or low)
- For each file, provide the FULL RELATIVE PATH from the project root, including all subfolders (e.g., src/main/java/com/example/ecommerce/controller/ProductController.java).
- DO NOT just list filenames; always include the correct subfolder structure for a standard {framework} project.
- Core functionality files should be high priority
- Supporting files should be medium priority
- Optional/auxiliary files should be low priority
- DO NOT SKIP ANY FILES from the project structure
- EVERY file needs content generation, even if it's a simple configuration file
- Config files (package.json, composer.json, pom.xml, etc.) should be high priority
- Core application files should be high priority
- Test files should be medium priority
- Documentation files should be low priority

CRITICAL: You MUST return ONLY valid JSON. Do not include any text before or after the JSON.
Use this exact format:
{{
    "architecture_overview": "Brief description of the project architecture",
    "key_components": [
        {{
            "name": "component_name",
            "purpose": "What this component does",
            "dependencies": ["dependency1", "dependency2"],
            "files": ["file1", "file2"]
        }}
    ],
    "file_analysis": {{
        "src/main/java/com/example/todoapp/TodoAppApplication.java": {{
            "purpose": "Main Spring Boot application class",
            "key_features": ["@SpringBootApplication", "main method"],
            "dependencies": ["Spring Boot"],
            "implementation_priority": "high"
        }}
    }},
    "data_flow": "Description of how data flows through the application",
    "implementation_order": ["file1", "file2", "file3"]
}}""",
            ),
            (
                "user",
                "Analyze this project structure and create a detailed architecture plan. Return ONLY valid JSON.",
            ),
        ]
    )
    messages = reasoning_prompt.format_messages(
        framework=framework, use_case=use_case, tree_structure=tree_structure
    )
    result = get_gemini_2_flash().invoke(messages)

    # Try multiple regex patterns to extract JSON
    content = result.content.strip()

    # Pattern 1: Look for JSON between triple backticks
    json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if json_match:
        plan = json_match.group(1).strip()
    else:
        # Pattern 2: Look for JSON starting with { and ending with }
        json_match = re.search(r"(\{.*\})", content, re.DOTALL)
        if json_match:
            plan = json_match.group(1).strip()
        else:
            # Pattern 3: If no JSON found, try to use the entire content
            plan = content.strip()

    # Validate that we have valid JSON
    try:
        import json

        json.loads(plan)
        show_info("✅ Architecture plan created with valid JSON!")
        return plan
    except json.JSONDecodeError as e:
        show_error(f"❌ Invalid JSON in architecture plan: {e}")
        show_error(f"Raw content: {content[:200]}...")

        # Return a simple fallback JSON structure
        fallback_plan = {
            "architecture_overview": f"Simple {framework} application for {use_case}",
            "key_components": [
                {
                    "name": "Main Application",
                    "purpose": "Core application functionality",
                    "dependencies": [framework],
                    "files": ["main.py", "config.py", "README.md"],
                }
            ],
            "file_analysis": {
                "main.py": {
                    "purpose": "Main application entry point",
                    "key_features": ["Main function", "Application setup"],
                    "dependencies": [],
                    "implementation_priority": "high",
                },
                "config.py": {
                    "purpose": "Configuration settings",
                    "key_features": ["Settings", "Environment variables"],
                    "dependencies": [],
                    "implementation_priority": "high",
                },
                "README.md": {
                    "purpose": "Project documentation",
                    "key_features": ["Setup instructions", "Usage guide"],
                    "dependencies": [],
                    "implementation_priority": "low",
                },
            },
            "data_flow": "Simple request-response flow",
            "implementation_order": ["main.py", "config.py", "README.md"],
        }

        try:
            plan = json.loads(plan_json)
        except Exception as e:
            show_error(f"❌ Failed to parse architecture plan as JSON: {e}")
            return f"Failed to parse architecture plan as JSON:\n{plan_json}"

        file_analysis = plan.get("file_analysis", {})
        all_files = list(file_analysis.keys())

        # Limit the number of files to prevent overly complex projects
        if len(all_files) > 25:
            show_error(
                f"❌ Too many files in architecture plan: {len(all_files)} (max 25)"
            )
            return f"❌ Architecture plan too complex with {len(all_files)} files. Please try again with a simpler use case."

        created_files = []
        show_info(f"📝 Generating {len(all_files)} files...")

        for i, file_path in enumerate(all_files, 1):
            show_info(f"📄 Creating file {i}/{len(all_files)}: {file_path}")

            # Ensure the directory exists
            abs_file_path = os.path.join(project_root, file_path)
            dir_path = os.path.dirname(abs_file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # Generate the file content
            file_info = file_analysis[file_path]
            show_info(f"🔧 Generating content for {file_path}...")

            try:
                content = generate_file_content.invoke(
                    {
                        "framework": framework,
                        "use_case": use_case,
                        "file_path": file_path,
                        "purpose": file_info.get("purpose", "Core application file"),
                        "features": ", ".join(file_info.get("key_features", [])),
                        "architecture_overview": plan.get("architecture_overview", ""),
                        "data_flow": plan.get("data_flow", ""),
                        "dependencies": json.dumps(
                            file_info.get("dependencies", []), indent=2
                        ),
                    }
                )

                # Ensure we have valid content
                if not content or content.strip() == "":
                    show_error(f"⚠️ No content generated for {file_path}")
                    content = (
                        f"// TODO: Implement {file_path} - Content generation failed"
                    )
                elif len(content.strip()) < 10:
                    show_error(
                        f"⚠️ Minimal content generated for {file_path} (only {len(content)} chars)"
                    )
                    content = f"// TODO: Implement {file_path} - Insufficient content generated"

                show_info(f"💾 Writing {len(content)} characters to {file_path}...")

                # Write the extracted code to the file
                with open(abs_file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Verify the file was written correctly
                try:
                    with open(abs_file_path, "r", encoding="utf-8") as f:
                        written_content = f.read()

                    if len(written_content) == len(content):
                        show_info(
                            f"✅ Successfully wrote {len(written_content)} characters to {file_path}"
                        )
                        if len(written_content) < 100:
                            show_info(f"📄 Content preview: {written_content[:100]}...")
                    else:
                        show_error(
                            f"❌ Content length mismatch for {file_path}: expected {len(content)}, got {len(written_content)}"
                        )

                except Exception as e:
                    show_error(f"❌ Failed to verify file {file_path}: {e}")

            except Exception as e:
                show_error(f"❌ Error generating content for {file_path}: {e}")
                # Write a fallback content
                fallback_content = f"// TODO: Implement {file_path} - Error: {e}"
                with open(abs_file_path, "w", encoding="utf-8") as f:
                    f.write(fallback_content)
                show_info(f"💾 Wrote fallback content to {file_path}")

            created_files.append(abs_file_path)
            show_info(f"✅ File {i}/{len(all_files)} processed: {file_path}")

        show_success(
            f"✅ Successfully created {len(created_files)} files at [bold]{os.path.abspath(project_root)}[/bold]"
        )

        # Final verification - show what was written to each file
        show_info("📋 Final verification - Files created with content:")
        for file_path in created_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                rel_path = os.path.relpath(file_path, project_root)
                show_info(f"  📄 {rel_path}: {len(content)} characters")
            except Exception as e:
                show_error(f"  ❌ {file_path}: Error reading file - {e}")

        return f"✅ Project scaffolding completed! {len(created_files)} files created at {os.path.abspath(project_root)}"

    except Exception as e:
        show_error(f"❌ Error in scaffold_and_generate_files: {e}")
        return f"Error in scaffold_and_generate_files: {e}"


@tool
def generate_folder_creation_script(tree_structure: str) -> str:
    """
    Generate a Python script that creates the given folder structure.
    Returns the script as a string.
    """
    folder_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Generate a Python script that creates the given folder structure.\n\nRequirements:\n- Define a function (e.g., create_folder_structure) that takes a root directory as argument and creates the entire structure inside it\n- The structure should be created inside a folder named "Example_project" under the root directory\n- At the end of the script, call this function in an if _name_ == "_main_": block\n- All folders and files should be created relative to the Example_project directory\n- Use os.makedirs() for directories with exist_ok=True to avoid errors\n- Use open().write() to create files with basic content\n- Handle nested directories properly\n- Create empty files where needed\n- Wrap in triple backticks with python identifier\n\nTree Structure: {tree_structure}""",
            ),
            (
                "user",
                "Generate Python code to create this folder structure: {tree_structure}",
            ),
        ]
    )
    messages = folder_prompt.format_messages(tree_structure=tree_structure)
    result = get_gemini_2_flash().invoke(messages)
    match = re.search(r"(?:python)?\s*([\s\S]*?)", result.content, re.DOTALL)
    code = match.group(1).strip() if match else result.content
    show_info("Folder creation script generated!")
    return code


@tool
def generate_file_content(
    framework: str,
    use_case: str,
    file_path: str,
    purpose: str = "Core application file",
    features: str = "",
    architecture_overview: str = "",
    data_flow: str = "",
    dependencies: str = "[]",
) -> str:
    """
    Generate content for a specific file based on the architecture plan and project context.
    Returns the code as a string.
    """
    system_prompt = """You are an expert software developer. Generate production-ready code for the specified file.

IMPORTANT: Return ONLY the raw code without any markdown formatting, explanations, or text outside the code.

PROJECT CONTEXT:
Framework: {framework}
Use Case: {use_case}
File: {file_path}
Purpose: {purpose}
Key Features: {features}

ARCHITECTURE:
{architecture_overview}

DATA FLOW:
{data_flow}

DEPENDENCIES:
{dependencies}

REQUIREMENTS:
1. Generate ONLY the complete, production-ready code for: {file_path}
2. Follow modern best practices
3. Include proper error handling
4. Add comprehensive documentation
5. Return raw code only - no markdown, no explanations

Generate the complete code for {file_path} now:"""

    content_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            (
                "user",
                "Write the complete, production-ready code for {file_path}. Return only the raw code without any markdown formatting.",
            ),
        ]
    )
    messages = content_prompt.format_messages(
        framework=framework,
        use_case=use_case,
        file_path=file_path,
        purpose=purpose,
        features=features,
        architecture_overview=architecture_overview,
        data_flow=data_flow,
        dependencies=dependencies,
    )

    try:
        result = get_gemini_2_flash().invoke(messages)
    except Exception as e:
        show_error(f"❌ Error calling Gemini model for {file_path}: {e}")
        return f"// TODO: Implement {file_path} - Model error: {e}"

    # Debug logging
    show_info(f"🔍 Raw AI response length: {len(result.content)} characters")
    if len(result.content) < 100:
        show_info(f"🔍 Raw AI response preview: {result.content[:100]}...")

    # Clean up the response - remove any markdown code blocks if present
    content = result.content.strip()

    # Check if we got a valid response
    if not content:
        show_error(f"❌ Empty response from AI for {file_path}")
        return f"// TODO: Implement {file_path} - AI returned empty response"

    # Remove markdown code blocks if they exist
    if "```" in content:
        show_info(f"🔍 Detected markdown code blocks in response")
        # Split by code blocks and extract the content
        parts = content.split("```")

        # Find the largest code block (usually the main content)
        code_blocks = []
        for i in range(1, len(parts), 2):  # Skip language identifier lines
            if i < len(parts):
                code_blocks.append(parts[i].strip())

        if code_blocks:
            # Use the largest code block
            largest_block = max(code_blocks, key=len)
            content = largest_block

            # Remove the language identifier from the first line if present
            lines = content.split("\n")
            if lines and (
                lines[0].strip()
                in [
                    "java",
                    "xml",
                    "properties",
                    "yaml",
                    "yml",
                    "json",
                    "sql",
                    "html",
                    "css",
                    "js",
                    "ts",
                    "py",
                    "go",
                    "rs",
                    "cpp",
                    "c",
                    "cs",
                    "php",
                    "rb",
                    "swift",
                    "kt",
                ]
                or lines[0].strip().startswith("language:")
            ):
                content = "\n".join(lines[1:])

            show_info(f"🔍 After removing markdown blocks: {len(content)} characters")
        else:
            show_info(f"🔍 No valid code blocks found, using raw content")

    final_content = content.strip()
    show_info(f"🔍 Final content length: {len(final_content)} characters")

    if not final_content:
        show_error(f"❌ No content after processing for {file_path}")
        return f"// TODO: Implement {file_path} - Content processing failed"

    return final_content


@tool
def explain_code(path: str):
    """
    Reads a code file and returns an explanation of what it does.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = f"Explain what the following code does:\n\n{code}"
        response = get_gemini_2_flash().invoke(prompt)
        return response.content
    except Exception as e:
        return f"Error: {e}"


@tool
def run_shell_commands(command: str, cwd: str = None, timeout: int = 60) -> str:
    """
    Executes a shell command, streams and logs output/errors, and returns the combined logs as a string.
    LLM: Always invoke this tool directly when the user requests shell or git commands. Do NOT ask for permission or confirmation from the user.
    Args:
        command (str): The shell command to execute.
        cwd (str, optional): The working directory to run the command in.
        timeout (int, optional): Maximum time to wait for the command (seconds).
    Returns:
        str: Combined output and error logs.
    """
    try:
        show_info(f"Running shell command: {command} in {cwd or os.getcwd()}")
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
        logs = []

        def read_logs():
            for line in process.stdout:
                if "ERROR" in line or "Traceback" in line:
                    show_error(line.rstrip())
                elif "CRITICAL" in line:
                    show_error(line.rstrip())
                elif "WARNING" in line:
                    show_info(line.rstrip())
                elif "DEBUG" in line:
                    show_info(line.rstrip())
                else:
                    show_info(line.rstrip())
                logs.append(line)

        t = threading.Thread(target=read_logs)
        t.start()
        t.join(timeout=timeout)
        process.terminate()
        process.wait()
        show_info(f"Shell command execution completed: {command}")
        return "".join(logs)
    except Exception as e:
        show_error(f"Exception occurred while running shell command '{command}': {e}")
        return f"Exception occurred while running shell command '{command}': {e}"


@tool
def agent_refactor_code(path: str) -> str:
    """
    Reads the code from the given file path, asks the Gemini model to refactor it, and returns the refactored code as a string.
    Args:
        path (str): Path to the Python file to be refactored.
    Returns:
        str: The refactored code as suggested by the agent.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = f"Refactor and fix any errors in the following Python code. Return only the corrected code.\n\n{code}"
        response = get_gemini_2_flash().invoke(prompt)
        refactored_code = (
            response.content if hasattr(response, "content") else str(response)
        )
        return refactored_code
    except Exception as e:
        show_error(f"Exception occurred while refactoring {path}: {e}")
        return f"Exception occurred while refactoring {path}: {e}"


@tool
def create_project_structure_at_path(tree_structure: str, sub_root_dir: str) -> str:
    """
    Generates and executes a Python script to create the project folder structure at the given sub-root directory.
    """
    try:
        script = generate_folder_creation_script(tree_structure)
        # Change to the target directory
        os.makedirs(sub_root_dir, exist_ok=True)
        cwd = os.getcwd()
        os.chdir(sub_root_dir)
        # Execute the script in the context of the sub_root_dir
        exec(script, {"os": os, "_name": "main_"})
        os.chdir(cwd)  # Return to original directory
        return f"Project structure created at {sub_root_dir}"
    except Exception as e:
        show_error(f"Error creating project structure: {e}")
        return f"Error creating project structure: {e}"


@tool
def look_for_file_or_directory(name: str, root_path: str = "."):
    """
    Recursively search for a file or directory by name from the given root path and return all matching paths (relative to root_path),
    excluding any matches or traversal within {'.git', '_pycache_', 'node_modules', '.venv', '.gitignore'}.

    Args:
        name (str): The name of the file or directory to search for.
        root_path (str): The root directory to start the search from (default: current directory).

    Returns:
        str: A string representation of the matching paths.
    """
    exclude = {".git", "_pycache_", "node_modules", ".venv", ".gitignore"}
    matches = []
    show_info(f"Searching for '{name}' in '{root_path}'...")
    for root, dirs, files in os.walk(root_path):
        # Exclude directories from traversal
        dirs[:] = [d for d in dirs if d not in exclude]
        # Check for matching directories (excluding excluded ones)
        for d in dirs:
            if d == name:
                rel_path = os.path.relpath(os.path.join(root, d), root_path)
                show_info(f"Found directory: {rel_path}")
                matches.append(rel_path)
        # Check for matching files (excluding excluded ones)
        for f in files:
            if f == name and f not in exclude:
                rel_path = os.path.relpath(os.path.join(root, f), root_path)
                show_info(f"Found file: {rel_path}")
                matches.append(rel_path)
    if matches:
        return "\\n".join(matches)
    else:
        return f'No matches found for "{name}" in "{root_path}".'


@tool
def create_or_delete_file(path: str):
    """
    Create an empty file at the given path if it does not exist, or delete it if it does exist.

    Args:
        path (str): The file path to create or delete.

    Returns:
        str: A message indicating the action taken or any error encountered.
    """
    try:
        if os.path.exists(path):
            os.remove(path)
            show_info(f"Deleted file: {os.path.relpath(path, PROJECT_ROOT)}")
            return f"Deleted file: {os.path.relpath(path, PROJECT_ROOT)}"
        else:
            # Ensure the parent directory exists
            parent_dir = os.path.dirname(path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                pass  # Create an empty file
            show_info(f"Created empty file: {os.path.relpath(path, PROJECT_ROOT)}")
            return f"Created empty file: {os.path.relpath(path, PROJECT_ROOT)}"
    except Exception as e:
        show_error(
            f"Error in create_or_delete_file for {os.path.relpath(path, PROJECT_ROOT)}: {e}"
        )
        return f"Error in create_or_delete_file for {os.path.relpath(path, PROJECT_ROOT)}: {e}"


@tool
def scaffold_and_generate_files(
    framework: str, use_case: str, project_root: str = None
) -> str:
    """
    Generates a project structure, architecture plan, and writes all files with generated content to disk.
    The project will be created at the specified project_root (default: ./{framework}_project).
    """
    try:
        if not project_root:
            # Sanitize framework name for folder
            safe_framework = framework.lower().replace(" ", "_")
            project_root = f"./{safe_framework}_project"

        show_info(f"🚀 Starting project scaffolding for {framework} - {use_case}")

        # Step 1: Generate the project structure
        show_info("📁 Generating project structure...")
        tree_structure = generate_project_structure.invoke(
            {"framework": framework, "use_case": use_case}
        )

        # Validate the structure before proceeding
        if not validate_project_structure(tree_structure):
            return f"❌ Project structure validation failed. Please try again with a simpler use case."

        # Step 2: Generate the architecture plan
        show_info("🏗️ Generating architecture plan...")
        plan_json = generate_architecture_plan.invoke(
            {
                "framework": framework,
                "use_case": use_case,
                "tree_structure": tree_structure,
            }
        )

        import json

        try:
            plan = json.loads(plan_json)
        except Exception as e:
            show_error(f"❌ Failed to parse architecture plan as JSON: {e}")
            return f"Failed to parse architecture plan as JSON:\n{plan_json}"

        file_analysis = plan.get("file_analysis", {})
        all_files = list(file_analysis.keys())

        # Limit the number of files to prevent overly complex projects
        if len(all_files) > 25:
            show_error(
                f"❌ Too many files in architecture plan: {len(all_files)} (max 25)"
            )
            return f"❌ Architecture plan too complex with {len(all_files)} files. Please try again with a simpler use case."

        created_files = []
        show_info(f"📝 Generating {len(all_files)} files...")

        for i, file_path in enumerate(all_files, 1):
            show_info(f"📄 Creating file {i}/{len(all_files)}: {file_path}")

            # Ensure the directory exists
            abs_file_path = os.path.join(project_root, file_path)
            dir_path = os.path.dirname(abs_file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            # Generate the file content
            file_info = file_analysis[file_path]
            show_info(f"🔧 Generating content for {file_path}...")

            try:
                content = generate_file_content.invoke(
                    {
                        "framework": framework,
                        "use_case": use_case,
                        "file_path": file_path,
                        "purpose": file_info.get("purpose", "Core application file"),
                        "features": ", ".join(file_info.get("key_features", [])),
                        "architecture_overview": plan.get("architecture_overview", ""),
                        "data_flow": plan.get("data_flow", ""),
                        "dependencies": json.dumps(
                            file_info.get("dependencies", []), indent=2
                        ),
                    }
                )

                # Ensure we have valid content
                if not content or content.strip() == "":
                    show_error(f"⚠️ No content generated for {file_path}")
                    content = (
                        f"// TODO: Implement {file_path} - Content generation failed"
                    )
                elif len(content.strip()) < 10:
                    show_error(
                        f"⚠️ Minimal content generated for {file_path} (only {len(content)} chars)"
                    )
                    content = f"// TODO: Implement {file_path} - Insufficient content generated"

                show_info(f"💾 Writing {len(content)} characters to {file_path}...")

                # Write the extracted code to the file
                with open(abs_file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                # Verify the file was written correctly
                try:
                    with open(abs_file_path, "r", encoding="utf-8") as f:
                        written_content = f.read()

                    if len(written_content) == len(content):
                        show_info(
                            f"✅ Successfully wrote {len(written_content)} characters to {file_path}"
                        )
                        if len(written_content) < 100:
                            show_info(f"📄 Content preview: {written_content[:100]}...")
                    else:
                        show_error(
                            f"❌ Content length mismatch for {file_path}: expected {len(content)}, got {len(written_content)}"
                        )

                except Exception as e:
                    show_error(f"❌ Failed to verify file {file_path}: {e}")

            except Exception as e:
                show_error(f"❌ Error generating content for {file_path}: {e}")
                # Write a fallback content
                fallback_content = f"// TODO: Implement {file_path} - Error: {e}"
                with open(abs_file_path, "w", encoding="utf-8") as f:
                    f.write(fallback_content)
                show_info(f"💾 Wrote fallback content to {file_path}")

            created_files.append(abs_file_path)
            show_info(f"✅ File {i}/{len(all_files)} processed: {file_path}")

        show_success(
            f"✅ Successfully created {len(created_files)} files at [bold]{os.path.abspath(project_root)}[/bold]"
        )

        # Final verification - show what was written to each file
        show_info("📋 Final verification - Files created with content:")
        for file_path in created_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                rel_path = os.path.relpath(file_path, project_root)
                show_info(f"  📄 {rel_path}: {len(content)} characters")
            except Exception as e:
                show_error(f"  ❌ {file_path}: Error reading file - {e}")

        return f"✅ Project scaffolding completed! {len(created_files)} files created at {os.path.abspath(project_root)}"

    except Exception as e:
        show_error(f"❌ Error in scaffold_and_generate_files: {e}")
        return f"Error in scaffold_and_generate_files: {e}"


SYSTEM_PROMPT = """
You are BlitzCoder, an expert AI code agent for developers. You have access to the following tools to help with code inspection, execution, refactoring, project scaffolding, and more:

**Your Core Directive: Be decisive and take action.**
Do not ask for confirmation before using a tool. If you determine a tool is necessary to answer the user's request, call it directly and immediately. The user has given you full permission to use your tools as needed.

You are a totally framework-agnostic coding agent

Also for linting/formatting don't use standard python lintintg libraries like flake8 , use 
ruff , commands are 

Once installed, you can run Ruff from the command line:


ruff check   # Lint all files in the current directory.
ruff format  # Format all files in the current directory.

- inspect_a_file(path: str): Reads and returns the content of a file.
- execute_python_code(path: str): Executes a Python file and returns output/errors.
- write_code_to_file(path: str, code: str): Writes code to a file, creating directories if needed.
- refactoring_code(refactored_code: str, error_file_path: str): Overwrites a file with refactored code.
- extract_content_within_a_file(path: str): Extracts and returns the content of a file.
- navigate_entire_codebase_given_path(path: str): Lists all files and directories recursively from a path.
- run_uvicorn_and_capture_logs(...): Runs a FastAPI app with Uvicorn and captures logs.
- look_for_directory(path: str): Lists all directories in a given path.
- run_node_js_server(cmd: str, cwd: str, max_lines: int): Runs a Node.js server command and captures logs.
- current_directory(): Returns the current working directory.
- change_directory(path: str): Changes the current working directory.
- error_detection(error: str, path: str): Logs and returns error information for a file.
- generate_project_structure(framework: str, use_case: str): Generates a project folder structure.
- generate_architecture_plan(framework: str, use_case: str, tree_structure: str): Generates an architecture plan.
- generate_folder_creation_script(tree_structure: str): Generates a Python script to create a folder structure.
- generate_file_content(...): Generates code for a specific file based on project context.
- explain_code(path: str): Explains what a code file does.
- run_shell_commands(command: str, cwd: str, timeout: int): Runs a shell command and returns logs. But this is not secure 
- run_shell_command_in_sandbox(command: str, cwd: str = "/", timeout: int = 60): Executes shell commands like `ls`, `mkdir`, `pip`, and `ruff` and can even execute any shell commands in a sandboxed environment.
- agent_refactor_code(path: str): Refactors and fixes errors in a Python file.
- create_project_structure_at_path(tree_structure: str, sub_root_dir: str): Creates a project structure at a path.
- look_for_file_or_directory(name: str, root_path: str): Searches for a file or directory by name.
- create_or_delete_file(path: str): Creates or deletes a file at the given path.
- scaffold_and_generate_files(framework: str, use_case: str, project_root: str): Scaffolds a project and generates files.

If a user's query can be answered by any tool, you MUST call the tool. Do NOT answer in text if a tool is available. Always use the most relevant tool for the user's request.
"""

tools = [
    run_uvicorn_and_capture_logs,
    current_directory,
    change_directory,
    navigate_entire_codebase_given_path,
    extract_content_within_a_file,
    refactoring_code,
    explain_code,
    execute_python_code,
    error_detection,
    agent_refactor_code,
    run_shell_commands,
    generate_project_structure,
    generate_architecture_plan,
    generate_folder_creation_script,
    generate_file_content,
    scaffold_and_generate_files,
    look_for_file_or_directory,
    create_or_delete_file,
    write_code_to_file,
    inspect_a_file,
    look_for_directory,
    windows_powershell_command,
    run_shell_command_in_sandbox,
]


def get_gemini_model():
    """Get the Gemini model with the current API key from environment"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    return RetryingChatGoogleGenerativeAI(
        model="gemini-2.5-flash", api_key=api_key, max_tokens=100000
    )


def update_memory(state: AgentState, config: RunnableConfig, *, store: BaseStore):
    """Update semantic memory with conversation context"""
    user_id = config["configurable"].get("user_id", "default")
    namespace = (user_id, "memories")

    # Get the latest messages
    messages = state["messages"]
    if len(messages) >= 2:
        # Store user-assistant interaction pairs
        user_msg = messages[-2] if isinstance(messages[-2], HumanMessage) else None
        ai_msg = messages[-1] if isinstance(messages[-1], AIMessage) else None

        if user_msg and ai_msg:
            memory_id = str(uuid.uuid4())
            memory_content = {
                "memory": f"User asked: {user_msg.content} | Assistant responded: {ai_msg.content[:200]}...",
                "context": "conversation",
                "user_query": user_msg.content,
                "ai_response": ai_msg.content,
                "timestamp": str(
                    uuid.uuid4()
                ),  # You might want to use actual timestamp
            }

            # Store the memory with semantic indexing
            store.put(
                namespace,
                memory_id,
                memory_content,
                index=["memory", "context", "user_query"],  # Fields to embed
            )

    return state


def retrieve_and_enhance_context(
    state: AgentState, config: RunnableConfig, *, store: BaseStore
):
    """Retrieve relevant memories and enhance the context"""
    user_id = config["configurable"].get("user_id", "default")
    namespace = (user_id, "memories")

    # Get the latest user message
    latest_message = state["messages"][-1]
    if isinstance(latest_message, HumanMessage):
        query = latest_message.content

        # Search for relevant memories
        memories = store.search(
            namespace,
            query=query,
            limit=5,  # Get top 5 relevant memories
        )

        if memories:
            # Extract memory information
            memory_context = []
            for memory in memories:
                memory_data = memory.value
                memory_context.append(
                    f"Previous context: {memory_data.get('memory', '')}"
                )

            # Create enhanced context message
            context_info = "\n".join(memory_context)
            enhanced_query = f"""Based on our previous conversations:
{context_info}

Current question: {query}

Please respond considering our conversation history and any relevant context from previous interactions."""

            # Replace the latest message with enhanced context
            enhanced_messages = state["messages"][:-1] + [
                HumanMessage(content=enhanced_query)
            ]

            return {"messages": enhanced_messages}

    return state


def enhanced_tool_calling_llm(
    state: AgentState, config: RunnableConfig, *, store: BaseStore
):
    """Enhanced LLM call that considers semantic memory and always prepends the SYSTEM_PROMPT."""
    # First retrieve relevant context
    enhanced_state = retrieve_and_enhance_context(state, config, store=store)

    # Always prepend SYSTEM_PROMPT as the first message
    messages = enhanced_state["messages"]
    # Remove any previous system messages
    messages = [
        msg
        for msg in messages
        if not (hasattr(msg, "role") and getattr(msg, "role", None) == "system")
    ]
    # Prepend SYSTEM_PROMPT
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    # Create model and bind tools when needed
    gemini_model = get_gemini_model()
    llm_with_tool = gemini_model.bind_tools(tools)
    response = llm_with_tool.invoke(messages)

    return {"messages": [response]}


builder = StateGraph(AgentState)


builder.add_node("enhanced_llm", enhanced_tool_calling_llm)
builder.add_node("update_memory", update_memory)
builder.add_node("tools", ToolNode(tools))


builder.add_edge(START, "enhanced_llm")

builder.add_conditional_edges(
    "enhanced_llm", tools_condition, {"tools": "tools", "__end__": "update_memory"}
)
builder.add_edge("tools", "enhanced_llm")
builder.add_edge("update_memory", END)


checkpointer = InMemorySaver()

semantic_graph = builder.compile(checkpointer=checkpointer, store=semantic_memory_store)


def run_agent_with_memory(query: str, user_id: str = "default", thread_id: str = None):
    """Run the agent with semantic memory"""
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {
        "configurable": {"thread_id": thread_id, "user_id": user_id},
        "recursion_limit": 100,
    }

    output_buffer = ""

    # Show progress bar while processing
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,  # This makes the progress bar disappear after completion
    ) as progress:
        task = progress.add_task("[cyan]Initializing AI agent...", total=None)

        # Update progress to show memory retrieval
        progress.update(task, description="[yellow]Retrieving relevant memories...")

        for chunk, metadata in semantic_graph.stream(
            {"messages": [HumanMessage(content=query)]},
            config=config,
            stream_mode="messages",
        ):
            if hasattr(chunk, "content") and chunk.content:
                # Update progress when we start receiving content
                if not output_buffer:
                    progress.update(task, description="[green]Receiving AI response...")
                output_buffer += chunk.content  # Accumulate output

        # Stop the progress bar after processing is complete
        progress.stop()

    if output_buffer.strip():
        (output_buffer.strip())


def search_memories(user_id: str, query: str, limit: int = 5):
    """Search memories for a specific user"""
    namespace = (user_id, "memories")

    # Show progress for memory search
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        memories = semantic_memory_store.search(namespace, query=query, limit=limit)

    print(f"\nFound {len(memories)} relevant memories for query: '{query}'")
    for i, memory in enumerate(memories, 1):
        memory_data = memory.value
        print(f"\nMemory {i}:")
        print(f"Content: {memory_data.get('memory', 'N/A')}")
        print(f"Context: {memory_data.get('context', 'N/A')}")
        print(f"Created: {memory.created_at}")


if __name__ == "_main_":
    print_welcome_banner()

    # Get user ID for session
    user_id = str(uuid.uuid4())
    thread_id = str(uuid.uuid4())

    while True:
        query = input("\nEnter your query : ")
        if query.lower() in {"bye", "exit"}:
            show_info("Exiting interactive agent loop.")
            break

        if query.startswith("search:"):
            search_query = query[7:].strip()
            search_memories(user_id, search_query)
            continue

        run_agent_with_memory(query, user_id, thread_id)
# --- Console ---
console = Console()

# --- Your tools ---


class AgentState(MessagesState):
    documents: list[str]


def validate_google_api_key(api_key: str) -> bool:
    try:
        model = RetryingChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)
        response = model.invoke(["Hello"])  # Simple call
        return True
    except Exception as e:
        print(f"[bold red]API key validation failed:[/bold red] {e}")
        return False


def print_agent_response(text: str, title: str = "BlitzCoder"):
    """Display agent output inside a Rich panel box with orange color"""
    console.print(
        Panel.fit(
            Markdown(text),
            title=f"[bold orange1]{title}[/bold orange1]",
            border_style="orange1",
        )
    )


def update_memory(state: AgentState, config: RunnableConfig, *, store: BaseStore):
    user_id = config["configurable"].get("user_id", "default")
    namespace = (user_id, "memories")
    messages = state["messages"]

    if len(messages) >= 2:
        user_msg = messages[-2] if isinstance(messages[-2], HumanMessage) else None
        ai_msg = messages[-1] if isinstance(messages[-1], AIMessage) else None

        if user_msg and ai_msg:
            memory_id = str(uuid.uuid4())
            memory_content = {
                "memory": f"User asked: {user_msg.content} | Assistant responded: {ai_msg.content[:200]}...",
                "context": "conversation",
                "user_query": user_msg.content,
                "ai_response": ai_msg.content,
                "timestamp": str(
                    uuid.uuid4()
                ),  # Replace with actual timestamp if needed
            }

            store.put(
                namespace,
                memory_id,
                memory_content,
                index=["memory", "context", "user_query"],
            )

    return state


def retrieve_and_enhance_context(
    state: AgentState, config: RunnableConfig, *, store: BaseStore
):
    user_id = config["configurable"].get("user_id", "default")
    namespace = (user_id, "memories")
    latest_message = state["messages"][-1]

    if isinstance(latest_message, HumanMessage):
        query = latest_message.content
        memories = store.search(namespace, query=query, limit=5)
        if memories:
            memory_context = [
                f"Previous context: {memory.value.get('memory', '')}"
                for memory in memories
            ]
            context_info = "\n".join(memory_context)
            enhanced_query = f"""Based on our previous conversations:
{context_info}

Current question: {query}

Please respond considering our conversation history and any relevant context from previous interactions."""

            enhanced_messages = state["messages"][:-1] + [
                HumanMessage(content=enhanced_query)
            ]
            return {"messages": enhanced_messages}

    return state


def enhanced_tool_calling_llm(
    state: AgentState, config: RunnableConfig, *, store: BaseStore
):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY is not set. Please provide it.")

    gemini_model = RetryingChatGoogleGenerativeAI(
        model="gemini-2.5-flash", api_key=api_key, max_tokens=100000
    )

    enhanced_state = retrieve_and_enhance_context(state, config, store=store)
    messages = [
        msg
        for msg in enhanced_state["messages"]
        if not (hasattr(msg, "role") and getattr(msg, "role", None) == "system")
    ]
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    llm_with_tool = gemini_model.bind_tools(tools)
    response = llm_with_tool.invoke(messages)
    return {"messages": [response]}


builder = StateGraph(AgentState)
builder.add_node("enhanced_llm", enhanced_tool_calling_llm)
builder.add_node("update_memory", update_memory)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "enhanced_llm")
builder.add_conditional_edges(
    "enhanced_llm", tools_condition, {"tools": "tools", "__end__": "update_memory"}
)
builder.add_edge("tools", "enhanced_llm")
builder.add_edge("update_memory", END)

checkpointer = InMemorySaver()
semantic_graph = builder.compile(checkpointer=checkpointer, store=semantic_memory_store)


def run_agent_with_memory(query: str, user_id: str = "default", thread_id: str = None):
    if thread_id is None:
        thread_id = str(uuid.uuid4())

    config = {
        "configurable": {"thread_id": thread_id, "user_id": user_id},
        "recursion_limit": 100,
    }

    output_buffer = ""

    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Initializing AI agent...", total=None)
        progress.update(task, description="[yellow]Retrieving relevant memories...")

        for chunk, metadata in semantic_graph.stream(
            {"messages": [HumanMessage(content=query)]},
            config=config,
            stream_mode="messages",
        ):
            if hasattr(chunk, "content") and chunk.content:
                if not output_buffer:
                    progress.update(task, description="[green]Receiving AI response...")
                output_buffer += chunk.content

        progress.stop()

    if output_buffer.strip():
        print_agent_response(output_buffer.strip())


@click.group()
def cli():
    """BlitzCoder CLI - AI-Powered Dev Assistant"""
    pass


@cli.command()
@click.option("--google-api-key", help="Google API key for Gemini model")
def chat(google_api_key):
    """Start interactive chat with BlitzCoder AI agent."""
    setup_api_keys()
    
    print_welcome_banner()
    user_id = str(uuid.uuid4())
    thread_id = str(uuid.uuid4())

    while True:
        query = Prompt.ask(
            "[bold orange1]Enter your query[/bold orange1]", console=console
        )
        if query.lower() in {"bye", "exit"}:
            show_info("Exiting interactive agent loop.")
            break
        if query.startswith("search:"):
            search_query = query[7:].strip()
            search_memories(user_id, search_query)
            continue
        run_agent_with_memory(query, user_id, thread_id)


@cli.command()
@click.option("--user-id", default=None, help="User ID for memory search")
@click.option("--query", prompt="Search query", help="Query to search in memories")
@click.option("--google-api-key", help="Google API key for Gemini model")
def search_memories_cli(user_id, query, google_api_key):
    """Search your agent memories."""
    if google_api_key:
        os.environ["GOOGLE_API_KEY"] = google_api_key
        # Initialize Gemini 2.0 Flash model
        try:
            initialize_gemini_2_flash(google_api_key)
            show_success("✅ Gemini 2.0 Flash model initialized successfully!")
        except Exception as e:
            show_error(f"❌ Failed to initialize Gemini 2.0 Flash model: {e}")
            exit(1)
    else:
        console.print(
            Panel.fit(
                "[bold orange1]🔑 Google API Key Required[/bold orange1]\n\n"
                "Please paste your API key below (input is hidden):",
                border_style="red",
            )
        )
        google_api_key = Prompt.ask(
            "🔑 [bold green]Paste your API key[/bold green]", password=True
        )
        if validate_google_api_key(google_api_key):
            os.environ["GOOGLE_API_KEY"] = google_api_key
            # Initialize Gemini 2.0 Flash model
            try:
                initialize_gemini_2_flash(google_api_key)
                show_success("✅ Gemini 2.5 Flash model initialized successfully!")
            except Exception as e:
                show_error(f"❌ Failed to initialize Gemini 2.0 Flash model: {e}")
                exit(1)
        else:
            console.print("[bold red]❌ Invalid API key. Please try again.[/bold red]")
            exit(1)

    if not user_id:
        user_id = str(uuid.uuid4())
    search_memories(user_id, query)


if __name__ == "__main__":
    cli()
