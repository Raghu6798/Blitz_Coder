import os
import subprocess
import threading
from langchain_core.tools import tool

@tool
def run_shell_commands(command: str, cwd: str = None, timeout: int = 60) -> str:
    """
    Executes a shell command and returns the combined logs as a string.
    Args:
        command (str): The shell command to execute.
        cwd (str, optional): The working directory to run the command in.
        timeout (int, optional): Maximum time to wait for the command (seconds).
    Returns:
        str: Combined output and error logs.
    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
        logs = []

        def read_logs():
            for line in process.stdout:
                logs.append(line)

        t = threading.Thread(target=read_logs)
        t.start()
        t.join(timeout=timeout)
        process.terminate()
        process.wait()
        return "".join(logs)
    except Exception as e:
        return f"Exception occurred while running shell command '{command}': {e}"

if __name__ == "__main__":
    run_shell_commands()
