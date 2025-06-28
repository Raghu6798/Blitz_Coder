import os
from langchain_core.tools import tool

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
            return f"Deleted file: {path}"
        else:
            # Ensure the parent directory exists
            parent_dir = os.path.dirname(path)
            if parent_dir and not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                pass  # Create an empty file
            return f"Created empty file: {path}"
    except Exception as e:
        return f"Error in create_or_delete_file for {path}: {e}"

if __name__ == "__main__":
    create_or_delete_file()
