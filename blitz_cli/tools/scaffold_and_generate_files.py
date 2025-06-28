import os
from langchain_core.tools import tool

@tool
def scaffold_and_generate_files(
    framework: str, use_case: str, project_root: str = None
) -> str:
    """
    Generates a project structure, architecture plan, and writes all files with generated content to disk.
    The project will be created at the specified project_root (default: ./{framework}_project).
    """
    # try:
    #     if not project_root:
    #         # Sanitize framework name for folder
    #         safe_framework = framework.lower().replace(" ", "_")
    #         project_root = f"./{safe_framework}_project"
    #     # Step 1: Generate the project structure
    #     tree_structure = generate_project_structure.invoke(
    #         {"framework": framework, "use_case": use_case}
    #     )
    #     # Step 2: Generate the architecture plan
    #     plan_json = generate_architecture_plan.invoke(
    #         {
    #             "framework": framework,
    #             "use_case": use_case,
    #             "tree_structure": tree_structure,
    #         }
    #     )
    #     import json

    #     try:
    #         plan = json.loads(plan_json)
    #     except Exception:
    #         return f"Failed to parse architecture plan as JSON:\n{plan_json}"

    #     file_analysis = plan.get("file_analysis", {})
    #     all_files = list(file_analysis.keys())
    #     created_files = []

    #     for file_path in all_files:
    #         # Ensure the directory exists
    #         abs_file_path = os.path.join(project_root, file_path)
    #         dir_path = os.path.dirname(abs_file_path)
    #         if dir_path:
    #             os.makedirs(dir_path, exist_ok=True)
    #         # Generate the file content
    #         file_info = file_analysis[file_path]
    #         content = generate_file_content.invoke(
    #             {
    #                 "framework": framework,
    #                 "use_case": use_case,
    #                 "file_path": file_path,
    #                 "purpose": file_info.get("purpose", "Core application file"),
    #                 "features": ", ".join(file_info.get("key_features", [])),
    #                 "architecture_overview": plan.get("architecture_overview", ""),
    #                 "data_flow": plan.get("data_flow", ""),
    #                 "dependencies": json.dumps(
    #                     file_info.get("dependencies", []), indent=2
    #                 ),
    #             }
    #         )
    #         # Write the file
    #         with open(abs_file_path, "w", encoding="utf-8") as f:
    #             f.write(content)
    #         created_files.append(abs_file_path)

    #     show_success(f"{len(created_files)} files created at [bold]{os.path.abspath(project_root)}[/bold]")

    # except Exception as e:
    #     show_error(f"Error in scaffold_and_generate_files: {e}")
    #     return f"Error in scaffold_and_generate_files: {e}"
    return f'framework:{framework},use_case:{use_case},project_root:{project_root}'

if __name__ == "__main__":
    scaffold_and_generate_files()
