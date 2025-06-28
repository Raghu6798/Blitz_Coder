from langchain_core.tools import tool
from langchain.prompts import ChatPromptTemplate

@tool
def generate_architecture_plan(
    framework: str, use_case: str, tree_structure: str
) -> str:
    """
    Generate a comprehensive architecture plan for the given project structure.
    Returns the plan as a JSON string.
    """
    reasoning_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """
You are an expert software architect with deep reasoning capabilities.

Analyze the given project structure and create a comprehensive architecture plan.

Your task:
1. ANALYZE the folder structure deeply
2. UNDERSTAND the relationships between components
3. PLAN the data flow and dependencies
4. IDENTIFY ALL files that need implementation
5. DETERMINE the content strategy for EACH file

Framework: {framework}
Use Case: {use_case}
Project Structure:
{tree_structure}

CRITICAL REQUIREMENTS:
- Every file in the project structure MUST be included in file_analysis
- Every file MUST have an implementation_priority (high, medium, or low)
- For each file, provide the FULL RELATIVE PATH from the project root, including all subfolders (e.g., src/main/java/com/example/ecommerce/controller/ProductController.java).
- DO NOT just list filenames; always include the correct subfolder structure for a standard {framework} project.
- Core functionality files should be high priority
- Supporting files should be medium priority
- Optional/auxiliary files should be low priority
- DO NOT SKIP ANY FILES from the project structure
- EVERY file needs content generation, even if it's a simple configuration file
- Config files (package.json, composer.json, pom.xml, etc.) should be high priority
- Core application files should be high priority
- Test files should be medium priority
- Documentation files should be low priority

Wrap your analysis in triple backticks as structured JSON with this format:
{{
    "architecture_overview": "...",
    "key_components": [
        {{
            "name": "component_name",
            "purpose": "...",
            "dependencies": ["..."],
            "files": ["..."]
        }}
    ],
    "file_analysis": {{
        "filename": {{
            "purpose": "...",
            "key_features": ["..."],
            "dependencies": ["..."],
            "implementation_priority": "high|medium|low"
        }}
    }},
    "data_flow": "...",
    "implementation_order": ["..."]
}}
""",
            ),
            (
                "user",
                "Analyze this project structure and create a detailed architecture plan.",
            ),
        ]
    )
    messages = reasoning_prompt.format_messages(
        framework=framework, use_case=use_case, tree_structure=tree_structure
    )
    # result = mistral_small.invoke(messages)
    # match = re.search(r"```(?:json)?\s*([\s\S]*?)```", result.content, re.DOTALL)
    # plan = match.group(1).strip() if match else result.content
    # show_info("Architecture plan created!")
    return f'framework:{framework} , use_case:{use_case}, tree_structure:{tree_structure}'

if __name__ == "__main__":
    generate_architecture_plan()
