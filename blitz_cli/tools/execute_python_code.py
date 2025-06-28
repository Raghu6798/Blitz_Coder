import os
import subprocess
import threading
from langchain_core.tools import tool

@tool
def execute_python_code(path: str):
    """
    Args (str): Path of the python file to be executed
    Returns (str): Output and errors of the python file execution, logged and returned as a string
    """
    try:
        print(f"Executing Python file: {path}")
        process = subprocess.Popen(
            ["python", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
        )
        logs = []

        def read_logs():
            for line in process.stdout:
                if "ERROR" in line or "Traceback" in line:
                    print(line.rstrip())
                elif "CRITICAL" in line:
                    print(line.rstrip())
                elif "WARNING" in line:
                    print(line.rstrip())
                elif "DEBUG" in line:
                    print(line.rstrip())
                else:
                    print(line.rstrip())
                logs.append(line)

        t = threading.Thread(target=read_logs)
        t.start()
        t.join(timeout=30)  # Wait for logs or timeout
        process.terminate()
        process.wait()
        print(f"Execution of {path} completed.")
        return "".join(logs)
    except Exception as e:
        print(f"Exception occurred while executing {path}: {e}")
        return f"Exception occurred while executing {path}: {e}"

if __name__ == "__main__":
    execute_python_code()
