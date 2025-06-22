import os  # ← Fixed typo from "mport os"

import re
import shutil
import subprocess
from typing import Optional
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_sambanova import ChatSambaNovaCloud

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # ← Fixed from 'file' to '__file__'

def slugify(text: str, max_length: int = 50) -> str:
    """
    Converts a string into a URL-friendly slug and truncates it to a maximum length.
    """
    slug = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return slug[:max_length].strip('-')

def determine_project_structure(user_query: str) -> str:
    """Generate project structure from user query using LLM"""
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", '''Based on the complexity of the user's desired Next JS or React project,
generate a scalable production-ready project folder tree structure.
No code required - just generate the project folder structure.

IMPORTANT:
- For Next.js (App Router, Next.js 13+), the main landing page must be at app/page.tsx.
- For Next.js (Pages Router), the main landing page must be at pages/index.tsx.
- For React (Vite, CRA, etc.), the main landing page must be at src/App.tsx.
- Always include the correct entry point for the landing page according to the framework.
- Include all necessary config files (package.json, tsconfig.json, next.config.js/json, etc.)
'''),
        ("user", "{user_query}")
    ])

    CodeAgent = ChatSambaNovaCloud(
        model="Llama-4-Maverick-17B-128E-Instruct",
        sambanova_api_key=os.getenv("SAMBANOVA_API_KEY")
    )

    repo_agent_chain = prompt_template | CodeAgent
    response = repo_agent_chain.invoke({"user_query": user_query})

    # Extract content between triple backticks
    pattern = r"```(?:\w+)?\n(.*?)```"  # ← Fixed backtick regex
    match = re.search(pattern, response.content, re.DOTALL)
    print(match)
    return match.group(1).strip() if match else response.content

def get_code_to_generate_structure(tree_text: str, project_path: str) -> str:
    """Use LLM to generate Python code that creates the given folder structure at the custom project directory."""
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", f"""You are a Python expert. Given a UNIX-style folder tree of a project,
write Python code that will recreate the same folder and file structure on disk using os.makedirs, ignore (...) as it
doesn't give permission to create folders.
The code must be minimal, using only built-in Python modules.
All folders and files must be created relative to this custom project directory: {project_path}
Wrap the code inside triple backticks and do not explain it."""),
        ("user", "{tree_text}")
    ])

    CodeAgent = ChatSambaNovaCloud(
        model="Llama-4-Maverick-17B-128E-Instruct",
        sambanova_api_key=os.getenv("SAMBANOVA_API_KEY")
    )

    chain = prompt_template | CodeAgent
    response = chain.invoke({"tree_text": tree_text})

    # Extract the code from triple backticks
    match = re.search(r"```(?:python)?\n(.*?)```", response.content, re.DOTALL)
    return match.group(1).strip() if match else response.content

def find_all_files(project_root: str):
    """Recursively find all files in the project root (not just .tsx)."""
    all_files = []
    for dirpath, _, filenames in os.walk(project_root):
        for f in filenames:
            all_files.append(os.path.join(dirpath, f))  # ← filled gap
    return all_files


if __name__ == "__main__":
    print("Which package manager do you want to use?")
    print("1. npm")
    print("2. yarn")
    print("3. pnpm")
    print("4. bun")
    pm_choice = input("Enter the number (1-4): ").strip()

    if pm_choice == "1":
        package_manager = "npm"
    elif pm_choice == "2":
        package_manager = "yarn"
    elif pm_choice == "3":
        package_manager = "pnpm"
    elif pm_choice == "4":
        package_manager = "bun"
    else:
        print("Invalid choice, defaulting to npm.")
        package_manager = "npm"

    user_query = input("What do you want to build?: ")
    project_name = slugify(user_query)
    project_path = os.path.join(ROOT_DIR, project_name)

    if os.path.exists(project_path):
        print(f"❌ Project directory '{project_name}' already exists.")
        print("Please provide a different project description or delete the existing directory.")
    else:
        print(f"✨ Creating new project directory: {project_path}")
        os.makedirs(project_path)

        tree_structure = determine_project_structure(user_query)
        print(tree_structure)
        print("🧠 Sending codebase structure tree to LLM...\n")
        python_code = get_code_to_generate_structure(tree_structure, project_path)
        print("🧾 Python Code to Recreate the Structure:\n")
        print(python_code)

        should_run = input("Do you want to execute the generated code to create the structure? (y/n): ").strip().lower()
        if should_run == 'y':
            try:
                exec(python_code, {"__file__": __file__, "ROOT_DIR": ROOT_DIR, "os": os, "shutil": shutil, "project_path": project_path})
                print("✅ Project structure created successfully!")
            except Exception as e:
                print(f"❌ Error executing generated code: {e}")
        else:
            print("Execution cancelled.")

        max_retries = 5
        retry_count = 0
        error_logs = ""

        while retry_count < max_retries:
            # After structure is created, find all files
            all_files = find_all_files(project_path)
            print(f"Found {len(all_files)} files in the project folder.")

            if not all_files:
                print("🤷 No files were created in the project structure. Nothing to generate.")
                break

            # Generate code for all files, passing error_logs to the LLM
            generate_code_for_all_files(all_files, tree_structure, user_query, project_path, package_manager, error_logs)

            # Install dependencies
            print(f"\n📦 Installing dependencies with {package_manager}...")
            try:
                if package_manager == "bun":
                    install_cmd = [package_manager, "install"]
                else:
                    install_cmd = [package_manager, "install"]

                install_proc = subprocess.run(install_cmd, cwd=project_path, capture_output=True, text=True)

                if install_proc.returncode != 0 and install_proc.stderr:
                    print(f"❌ Dependency installation failed:\n{install_proc.stderr}")
                    error_logs = install_proc.stderr
                    retry_count += 1
                    continue
            except Exception as e:
                print(f"❌ Exception during dependency installation: {e}")
                error_logs = str(e)
                retry_count += 1
                continue

            # Start dev server
            if package_manager == "npm":
                dev_cmd = ["npm", "run", "dev"]
            elif package_manager == "yarn":
                dev_cmd = ["yarn", "dev"]
            elif package_manager == "pnpm":
                dev_cmd = ["pnpm", "dev"]
            elif package_manager == "bun":
                dev_cmd = ["bun", "run", "dev"]
            else:
                dev_cmd = ["npm", "run", "dev"]

            print("\n🚀 Starting your app...")
            dev_proc = subprocess.run(dev_cmd, cwd=project_path, capture_output=True, text=True)

            if dev_proc.returncode != 0 and dev_proc.stderr:
                if "error" in dev_proc.stderr.lower():
                    print(f"❌ Dev server failed to start:\n{dev_proc.stderr}")
                    error_logs = dev_proc.stderr
                    retry_count += 1
                    continue

            print("✅ App started successfully!")
            break
        else:
            print("❌ Max retries reached. Please check the logs and debug manually.")