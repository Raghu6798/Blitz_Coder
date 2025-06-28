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
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, BarColumn, TimeElapsedColumn
from rich.text import Text
from rich.table import Table
from rich.live import Live
import questionary


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
from langchain_openai import OpenAIEmbeddings, ChatOpenAI

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import AgentSettings

load_dotenv()

# Configure loguru for colorful output (default is colorful in terminal)
logger.add(
    lambda msg: print(msg, end=""),
    colorize=True,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <green>{message}</green>"
    if "INFO" in "{level}"
    else "<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>",
)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
# @retry(
#     stop=stop_after_attempt(3),
#     wait=wait_fixed(2),
#     retry=retry_if_exception_type((requests.exceptions.RequestException,)),
#     reraise=True,
# )
# def init_langfuse():
#     return Langfuse(
#         public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
#         secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
#         host="https://us.cloud.langfuse.com",
#     )


# try:
#     langfuse = init_langfuse()
#     langfuse_handler = CallbackHandler()
# except Exception as e:
#     logger.warning(f"Langfuse initialization failed after retries: {e}")
#     langfuse = None
#     langfuse_handler = None


console = Console()


def print_welcome_banner():
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
        justify="center"
    )
    panel = Panel(
        banner_text,
        title="[bold orange1]⚡ BLITZCODER CLI[/bold orange1]",
        subtitle="[orange1]AI-Powered Dev Assistant[/orange1]",
        border_style="orange1",
        width=140,
        expand=True,
        padding=(2, 0)
    )
    console.print(panel)

def show_success(msg):
    console.print(Panel(f"[green]✅ {msg}", title="Success", style="green"))

def show_error(msg):
    console.print(Panel(f"[red]❌ {msg}", title="Error", style="red"))

def show_info(msg):
    console.print(Panel(f"[cyan]{msg}", title="Info", style="cyan"))

    
def print_agent_response(text: str, title: str = "BlitzCoder"):
    """Display agent output inside a Rich panel box with orange color"""
    console.print(Panel.fit(Markdown(text), title=f"[bold orange1]{title}[/bold orange1]", border_style="orange1"))


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
    with Progress(SpinnerColumn(), "[progress.description]{task.description}", BarColumn(), TimeElapsedColumn()) as progress:
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
            bufsize=1
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


# Semantic memory store for user memories, using Qwen3 embeddings
semantic_memory_store = InMemoryStore(
    index={
        "embed": OpenAIEmbeddings(
            base_url="https://api.novita.ai/v3/openai",
            api_key=os.getenv("NOVITA_API_KEY"),
            model="qwen/qwen3-embedding-8b",
        ),
        "dims": 4096,  # Qwen3 embedding dimension
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
    response = gemini.invoke(prompt)
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
        show_info(f"Extracting content from file: {os.path.relpath(path, PROJECT_ROOT)}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        show_info(f"Successfully extracted content from {os.path.relpath(path, PROJECT_ROOT)}")
        return content
    except FileNotFoundError:
        show_error(f"File not found: {os.path.relpath(path, PROJECT_ROOT)}")
        return f"Error: File not found: {os.path.relpath(path, PROJECT_ROOT)}"
    except UnicodeDecodeError:
        show_error(f"Could not decode file (not UTF-8): {os.path.relpath(path, PROJECT_ROOT)}")
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
                """You are a backend architecture expert. \
When given a backend framework and a use case, generate a realistic, production-ready project folder structure.\n\nRequirements:\n- STRICTLY follow {framework} conventions and file extensions\n- Wrap output in triple backticks\n- NO explanations, just the folder structure\n- Include all necessary files for a production app\n- Medium-to-large scale application\n\nFramework: {framework}\nUse Case: {use_case}""",
            ),
            (
                "user",
                "Generate the complete folder structure for {framework} framework for {use_case}",
            ),
        ]
    )
    messages = prompt_template.format_messages(framework=framework, use_case=use_case)
    result = mistral_small.invoke(messages)
    match = re.search(tree_pattern, result.content, re.DOTALL)
    tree_structure = match.group(1).strip() if match else result.content
    show_info(f"Generated Project Structure: {tree_structure}")
    return tree_structure


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
                """
You are an expert software architect with deep reasoning capabilities.

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

Wrap your analysis in triple backticks as structured JSON with this format:
{{
    "architecture_overview": "...",
    "key_components": [
        {{
            "name": "component_name",
            "purpose": "...",
            "dependencies": ["..."],
            "files": ["..."]
        }}
    ],
    "file_analysis": {{
        "filename": {{
            "purpose": "...",
            "key_features": ["..."],
            "dependencies": ["..."],
            "implementation_priority": "high|medium|low"
        }}
    }},
    "data_flow": "...",
    "implementation_order": ["..."]
}}
""",
            ),
            (
                "user",
                "Analyze this project structure and create a detailed architecture plan.",
            ),
        ]
    )
    messages = reasoning_prompt.format_messages(
        framework=framework, use_case=use_case, tree_structure=tree_structure
    )
    result = mistral_small.invoke(messages)
    match = re.search(r"(?:json)?\s*([\s\S]*?)", result.content, re.DOTALL)
    plan = match.group(1).strip() if match else result.content
    show_info("Architecture plan created!")
    return plan


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
    result = mistral_small.invoke(messages)
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
    system_prompt = """You are an expert software developer specializing in production-ready, scalable applications. Generate code for the specified file following modern best practices and patterns, regardless of programming language or framework.\n\n*PROJECT CONTEXT:\nFramework: {framework}\nUse Case: {use_case}\nFile: {file_path}\nPurpose: {purpose}\nKey Features: {features}\n\nCOMPLETE PROJECT ARCHITECTURE:\n{architecture_overview}\n\nCOMPONENT RELATIONSHIPS:\n{data_flow}\n\nFILE DEPENDENCIES:\n{dependencies}\n\n---\n\n3. SECURITY BEST PRACTICES:\n- Implement proper authentication/authorization if applicable\n- Use secure password handling where relevant\n- Implement secure token handling if needed\n- Use proper CORS configuration for web APIs\n- Input validation and sanitization\n\n4. CODE QUALITY:\n- Type annotations or equivalents and proper documentation\n- Clean code principles\n- Proper error handling\n- Logging and monitoring\n- Unit test coverage\n- Performance optimization\n\n5. PROJECT STRUCTURE:\n- Modular and maintainable code\n- Clear separation of concerns\n- Dependency injection where appropriate\n- Configuration management\n- Environment variable handling\n\n---\n🎯 FINAL INSTRUCTIONS:\n\nGenerate ONLY the complete, production-ready code for: **{file_path}*\n\nRequirements:\n1. Follow all architectural patterns above\n2. Include proper type annotations or equivalents\n3. Add comprehensive documentation\n4. Include proper error handling\n5. Ensure proper imports or dependencies\n6. Add logging where appropriate\n\nDo not include explanations or text outside the code block."""
    content_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", "Write the complete, production-ready code for {file_path}"),
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
    result = mistral_small.invoke(messages)
    match = re.search(r"(?:python)?\s*([\s\S]*?)", result.content, re.DOTALL)
    return match.group(1).strip() if match else result.content.strip()


@tool
def explain_code(path: str):
    """
    Reads a code file and returns an explanation of what it does.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = f"Explain what the following code does:\n\n{code}"
        response = gemini.invoke(prompt)
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
        response = gemini.invoke(prompt)
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
        show_error(f"Error in create_or_delete_file for {os.path.relpath(path, PROJECT_ROOT)}: {e}")
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
        # Step 1: Generate the project structure
        tree_structure = generate_project_structure.invoke(
            {"framework": framework, "use_case": use_case}
        )
        # Step 2: Generate the architecture plan
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
        except Exception:
            return f"Failed to parse architecture plan as JSON:\n{plan_json}"

        file_analysis = plan.get("file_analysis", {})
        all_files = list(file_analysis.keys())
        created_files = []

        for file_path in all_files:
            # Ensure the directory exists
            abs_file_path = os.path.join(project_root, file_path)
            dir_path = os.path.dirname(abs_file_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            # Generate the file content
            file_info = file_analysis[file_path]
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
            # Write the file
            with open(abs_file_path, "w", encoding="utf-8") as f:
                f.write(content)
            created_files.append(abs_file_path)

        show_success(f"{len(created_files)} files created at [bold]{os.path.abspath(project_root)}[/bold]")

    except Exception as e:
        show_error(f"Error in scaffold_and_generate_files: {e}")
        return f"Error in scaffold_and_generate_files: {e}"


SYSTEM_PROMPT = """
You are BlitzCoder, an expert AI code agent for developers. You have access to the following tools to help with code inspection, execution, refactoring, project scaffolding, and more:

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
- run_shell_commands(command: str, cwd: str, timeout: int): Runs a shell command and returns logs.
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
    windows_powershell_command
]

def get_gemini_model():
    """Get the Gemini model with the current API key from environment"""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash", 
        api_key=api_key, 
        max_tokens=100000
    )

CodeAgent = ChatGroq(
    model="qwen-qwq-32b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.2,
    max_tokens=100000,
    timeout=None,
    max_retries=2,
)

gemini = get_gemini_model()

mistral_small = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="meta-llama/llama-4-maverick-17b-128e-instruct",
)


llm_with_tool = gemini.bind_tools(tools)


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
    
    response = llm_with_tool.invoke(messages)

    return {"messages": [response]}


builder = StateGraph(AgentState)


builder.add_node("enhanced_llm", enhanced_tool_calling_llm)
builder.add_node("update_memory", update_memory)
builder.add_node("tools", ToolNode(tools))


builder.add_edge(START, "enhanced_llm")

builder.add_conditional_edges(
    "enhanced_llm", tools_condition, {"tools": "tools", "_end_": "update_memory"}
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
        "recursion_limit": 100
    }

    output_buffer = ""

    # Show progress bar while processing
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True  # This makes the progress bar disappear after completion
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
        print_agent_response(output_buffer.strip())



def search_memories(user_id: str, query: str, limit: int = 5):
    """Search memories for a specific user"""
    namespace = (user_id, "memories")
    
    # Show progress for memory search
    with Progress(
        SpinnerColumn(),
        "[progress.description]{task.description}",
        BarColumn(),
        TimeElapsedColumn(),
        console=console
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