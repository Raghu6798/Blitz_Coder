import os
from langchain_core.tools import tool

@tool
def windows_powershell_command(command: str) -> str:
    """
    Run a command in a windows PowerShell session and return the output.
    The session preserves state (variables, working directory, etc.) between calls.
    Args :
     command (str) : Windows Command to execute
    Return :
     Output (str) : Output after executing the command 
    """
    return ps.run_command(command)

if __name__ == "__main__":
    windows_powershell_command()
