import os
from langchain_core.tools import tool

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

if __name__ == "__main__":
    inspect_a_file()
