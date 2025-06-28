from langchain_core.tools import tool
from langchain.prompts import ChatPromptTemplate

@tool
def generate_folder_creation_script(tree_structure: str) -> str:
    """
    Generate a Python script that creates the given folder structure.
    Returns the script as a string.
    """
    folder_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Generate a Python script that creates the given folder structure.\n\nRequirements:\n- Define a function (e.g., create_folder_structure) that takes a root directory as argument and creates the entire structure inside it\n- The structure should be created inside a folder named \"Example_project\" under the root directory\n- At the end of the script, call this function in an if __name__ == \"__main__\": block\n- All folders and files should be created relative to the Example_project directory\n- Use os.makedirs() for directories with exist_ok=True to avoid errors\n- Use open().write() to create files with basic content\n- Handle nested directories properly\n- Create empty files where needed\n- Wrap in triple backticks with python identifier\n\nTree Structure: {tree_structure}""",
            ),
            (
                "user",
                "Generate Python code to create this folder structure: {tree_structure}",
            ),
        ]
    )
    messages = folder_prompt.format_messages(tree_structure=tree_structure)
    # result = mistral_small.invoke(messages)
    # match = re.search(r"```(?:python)?\s*([\s\S]*?)```", result.content, re.DOTALL)
    # code = match.group(1).strip() if match else result.content
    # show_info("Folder creation script generated!")
    return f'tree_structure : {tree_structure}'

if __name__ == "__main__":
    generate_folder_creation_script()
