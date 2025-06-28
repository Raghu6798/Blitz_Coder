import os
from langchain_core.tools import tool

@tool
def current_directory():
    """
    Get the current working directory path.

    Returns:
        str: The current working directory path.
    """
    return os.getcwd()

if __name__ == "__main__":
    current_directory()
