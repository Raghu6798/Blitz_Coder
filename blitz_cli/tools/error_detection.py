import os
from langchain_core.tools import tool

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
    # You can add more logic here to parse the error string and act accordingly
    return f"Error detected in {path}:\n{error}"

if __name__ == "__main__":
    error_detection()
