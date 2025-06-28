import os
from langchain_core.tools import tool


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
        exec(script, {"os": os, "__name__": "__main__"})
        os.chdir(cwd)  # Return to original directory
        return f"Project structure created at {sub_root_dir}"
    except Exception as e:
        show_error(f"Error creating project structure: {e}")
        return f"Error creating project structure: {e}"


if __name__ == "__main__":
    create_project_structure_at_path()
