import os
from langchain_core.tools import tool
from rich.tree import Tree
from rich.console import Console

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
    skip_dirs = {"__pycache__", ".git", ".venv", ".cache", "node_modules"}
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

if __name__ == "__main__":
    navigate_entire_codebase_given_path()
