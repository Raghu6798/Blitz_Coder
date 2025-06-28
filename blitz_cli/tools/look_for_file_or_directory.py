import os
from langchain_core.tools import tool

@tool
def look_for_file_or_directory(name: str, root_path: str = "."):
    """
    Recursively search for a file or directory by name from the given root path and return all matching paths
    Args:
        name (str): The name of the file or directory to search for.
        root_path (str): The root directory to start the search from (default: current directory).
    Returns:
        str: A string representation of the matching paths.
    """
    matches = []
    for root, dirs, files in os.walk(root_path):
        # Check for matching directories
        for d in dirs:
            if d == name:
                rel_path = os.path.relpath(os.path.join(root, d), root_path)
                matches.append(rel_path)
        # Check for matching files
        for f in files:
            if f == name:
                rel_path = os.path.relpath(os.path.join(root, f), root_path)
                matches.append(rel_path)
    if matches:
        return "\n".join(matches)
    else:
        return f'No matches found for "{name}" in "{root_path}".'

if __name__ == "__main__":
    look_for_file_or_directory()
