import os
from langchain_core.tools import tool

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
        print(f"Writing refactored code to {error_file_path}")
        with open(error_file_path, "w", encoding="utf-8") as file:
            file.write(refactored_code)
        print(f"Successfully wrote refactored code to {error_file_path}")
        return f"Successfully wrote refactored code to {error_file_path}"
    except Exception as e:
        print(f"Error writing to {error_file_path}: {e}")
        return f"Error writing to {error_file_path}: {e}"

if __name__ == "__main__":
    refactoring_code()
