import os
import re
from langchain_core.tools import tool

@tool
def write_code_to_file(path: str, code: str):
    """
    Write the provided code string to the specified file path, creating parent directories if needed.
    If the code contains class or function definitions, append an if __name__ == "__main__": block to run the function(s) or instantiate the class and invoke its methods.

    Args:
        path (str): The file path to write to.
        code (str): The code/content to write into the file.

    Returns:
        str: A message indicating success or any error encountered.
    """

    try:
        # Detect top-level classes and functions
        class_names = re.findall(r"^class\s+(\w+)\s*\(", code, re.MULTILINE)
        func_names = re.findall(r"^def\s+(\w+)\s*\(", code, re.MULTILINE)
        main_block = ""
        if class_names or func_names:
            main_block += '\n\nif __name__ == "__main__":\n'
            for cname in class_names:
                main_block += f"    obj = {cname}()\n"
                # Try to find methods (excluding __init__)
                method_matches = re.findall(
                    rf"^\s+def\s+(\w+)\s*\(", code, re.MULTILINE
                )
                for m in method_matches:
                    if m != "__init__":
                        main_block += f"    obj.{m}()\n"
            for fname in func_names:
                main_block += f"    {fname}()\n"
        # Append main block if needed
        final_code = code.rstrip() + main_block
        parent_dir = os.path.dirname(path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(final_code)
        print(f"Wrote code to file: {path}")
        return f"Successfully wrote code to {path} \n"
    except Exception as e:
        print(f"Error writing code to {path}: {e}")
        return f"Error writing code to {path}: {e}"

if __name__ == "__main__":
    write_code_to_file()
