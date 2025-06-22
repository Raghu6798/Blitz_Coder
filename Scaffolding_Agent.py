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