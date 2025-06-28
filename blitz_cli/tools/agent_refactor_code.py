import os
from langchain_core.tools import tool


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


if __name__ == "__main__":
    agent_refactor_code()
