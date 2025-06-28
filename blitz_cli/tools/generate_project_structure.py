from langchain_core.tools import tool
from langchain.prompts import ChatPromptTemplate

@tool
def generate_project_structure(framework: str, use_case: str) -> str:
    """
    Generate a realistic, production-ready project folder structure for the given framework and use case.
    Returns the folder tree as a string.
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a backend architecture expert. \
When given a backend framework and a use case, generate a realistic, production-ready project folder structure.\n\nRequirements:\n- STRICTLY follow {framework} conventions and file extensions\n- Wrap output in triple backticks\n- NO explanations, just the folder structure\n- Include all necessary files for a production app\n- Medium-to-large scale application\n\nFramework: {framework}\nUse Case: {use_case}""",
            ),
            (
                "user",
                "Generate the complete folder structure for {framework} framework for {use_case}",
            ),
        ]
    )
    messages = prompt_template.format_messages(framework=framework, use_case=use_case)
    # result = mistral_small.invoke(messages)
    # match = re.search(tree_pattern, result.content, re.DOTALL)
    # tree_structure = match.group(1).strip() if match else result.content
    # show_info(f"Generated Project Structure: {tree_structure}")
    # return tree_structure
    return f'framework:{framework} , use_case:{use_case}'

if __name__ == "__main__":
    generate_project_structure()
