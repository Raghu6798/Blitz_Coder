import os
from langchain_core.tools import tool

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
        print(f"Extracting content from file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"Successfully extracted content from {path}")
        return content
    except FileNotFoundError:
        return f"Error: File not found: {path}"
    except UnicodeDecodeError:
        return f"Error: Could not decode file (not UTF-8): {path}"
    except Exception as e:
        return f"Error reading file {path}: {e}"

if __name__ == "__main__":
    extract_content_within_a_file()
