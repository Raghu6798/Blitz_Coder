import os
from langchain_core.tools import tool

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
        return os.getcwd()
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    change_directory()
