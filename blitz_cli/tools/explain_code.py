import os
from langchain_core.tools import tool

@tool
def explain_code(path: str):
    """
    Reads a code file and returns an explanation of what it does.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        prompt = f"Explain what the following code does:\n\n{code}"
        # response = gemini.invoke(prompt)
        return f'path: {path}'
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    explain_code()
