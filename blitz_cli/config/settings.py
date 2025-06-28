from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Dict, Any, Optional



class AgentSettings(BaseSettings):
    # Use SettingsConfigDict for model configuration
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'  # Ignore extra fields from .env file
    )
    
    # Supported frameworks and their template files
    supported_frameworks: Dict[str, str] = {
        # Agentic AI Frameworks
        "agno": "Agentic_AI_Frameworks/agno_template.txt",
        "crew_ai": "Agentic_AI_Frameworks/crew_ai_template.txt",
        "google_agent_development_kit": "Agentic_AI_Frameworks/google_agent_development_kit_template.txt",
        "langgraph": "Agentic_AI_Frameworks/langraph_template.txt",
        "llama_index_agentic": "Agentic_AI_Frameworks/llama_index_template.txt",
        "mistral_agents_api": "Agentic_AI_Frameworks/mistral_agents_api_template.txt",
        "pydantic_ai": "Agentic_AI_Frameworks/pydantic_ai_template.txt",

        # App Development
        "flutter": "App Development/flutter_template.txt",
        "ionic": "App Development/ionic_template.txt",
        "react_native": "App Development/react_native_template.txt",

        # Backend
        "aspnet_core": "Backend/aspnet_core_template.txt",
        "django": "Backend/django_template.txt",
        "express": "Backend/express_template.txt",
        "fastapi": "Backend/fastapi_template.txt",
        "flask": "Backend/flask_template.txt",
        "koa": "Backend/koa_template.txt",
        "nest_js": "Backend/nest_js_template.txt",

        # Deep Learning
        "keras": "Deep Learning/keras_template.txt",
        "pytorch": "Deep Learning/pytorch_template.txt",
        "tensorflow": "Deep Learning/tensorflow_template.txt",

        # Frontend
        "alpine_js": "Frontend/alpinejs_template.txt",
        "angular": "Frontend/angular_template.txt",
        "astro": "Frontend/astro_template.txt",
        "gatsby": "Frontend/gatsby_template.txt",
        "lit": "Frontend/lit_template.txt",
        "next_js": "Frontend/nextjs_template.txt",
        "nuxt": "Frontend/nuxt_template.txt",
        "qwik": "Frontend/qwik_template.txt",
        "react": "Frontend/react_template.txt",
        "solid_js": "Frontend/solidjs_template.txt",
        "stencil": "Frontend/stencil_template.txt",
        "svelte": "Frontend/svelte_template.txt",
        "vue": "Frontend/vue_template.txt",

        # LLM Orchestration
        "langchain": "LLM Orchestration/langchain_template.txt",
        "llama_index": "LLM Orchestration/llama_index_template.txt",

        # Web3
        "solana": "Web3/solana.txt",
        "solidity": "Web3/solidity.txt",
    }

    # Tool enable/disable flags
    tools_enabled: Dict[str, bool] = {
        "powershell": True,
        "shell": True,
        "nodejs": True,
        "python_exec": True,
    }

    # Model configuration
    model_config_dict: Dict[str, Any] = {
        "default_model": "groq",
        "groq": {
            "model": "qwen-qwq-32b",
            "temperature": 0.2,
            "max_tokens": 100000,
        },
        "gemini": {
            "model": "gemini-2.0-flash",
            "max_tokens": 100000,
        },
    }

    # Recursion and memory
    recursion_limit: int = 100
    memory_size: int = 1000

    # API keys (can be loaded from env)
    groq_api_key: Optional[str] = None
    google_api_key: Optional[str] = None

    # System prompt as a class attribute (not a field)
    SYSTEM_PROMPT: str = """You are BlitzCoder, an expert AI code agent for developers. You have access to the following tools to help with code inspection, execution, refactoring, project scaffolding, and more:

- inspect_a_file(path: str): Reads and returns the content of a file.
- execute_python_code(path: str): Executes a Python file and returns output/errors.
- write_code_to_file(path: str, code: str): Writes code to a file, creating directories if needed.
- refactoring_code(refactored_code: str, error_file_path: str): Overwrites a file with refactored code.
- extract_content_within_a_file(path: str): Extracts and returns the content of a file.
- navigate_entire_codebase_given_path(path: str): Lists all files and directories recursively from a path.
- look_for_directory(path: str): Lists all directories in a given path.
- run_node_js_server(cmd: str, cwd: str, max_lines: int): Runs a Node.js server command and captures logs.
- current_directory(): Returns the current working directory.
- change_directory(path: str): Changes the current working directory.
- error_detection(error: str, path: str): Logs and returns error information for a file.
- generate_project_structure(framework: str, use_case: str): Generates a project folder structure.
- generate_architecture_plan(framework: str, use_case: str, tree_structure: str): Generates an architecture plan.
- generate_folder_creation_script(tree_structure: str): Generates a Python script to create a folder structure.
- generate_file_content(...): Generates code for a specific file based on project context.
- explain_code(path: str): Explains what a code file does.
- run_shell_commands(command: str, cwd: str, timeout: int): Runs a shell command and returns logs.
- agent_refactor_code(path: str): Refactors and fixes errors in a Python file.
- create_project_structure_at_path(tree_structure: str, sub_root_dir: str): Creates a project structure at a path.
- look_for_file_or_directory(name: str, root_path: str): Searches for a file or directory by name.
- create_or_delete_file(path: str): Creates or deletes a file at the given path.
- scaffold_and_generate_files(framework: str, use_case: str, project_root: str): Scaffolds a project and generates files.

If a user's query can be answered by any tool, you MUST call the tool. Do NOT answer in text if a tool is available. Always use the most relevant tool for the user's request."""


