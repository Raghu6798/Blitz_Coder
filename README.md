

# Blitzcode CLI

> **AI-powered code agent and utilities for developers**

![image](https://github.com/user-attachments/assets/39b5a459-18ce-4785-869e-adde1d2ed844)


## Overview
Blitzcode CLI is a powerful, AI-driven command-line tool that helps you scaffold, generate, inspect, and manage code projects at terminal speed. It leverages advanced language models and semantic memory to automate repetitive coding tasks, provide code explanations, refactor code, and much more—all from your terminal.

## Features
- **AI-powered project scaffolding** for popular frameworks (FastAPI, Spring Boot, Next.js, etc.)
- **Code generation** for files, modules, and entire architectures
- **Interactive agent loop** with model selection (Qwen, Gemini, Llama, etc.)
- **Semantic memory agent** for context-aware, human-in-the-loop workflows
- **File inspection, extraction, and search**
- **Run and debug Python and Node.js servers**
- **Code refactoring and explanation**
- **Colorized CLI help and output**
- **.agentignore support** to protect sensitive files

## Installation

1. Clone the repository:
   ```sh
   git clone <your-repo-url>
   cd blitz_cli
   ```
2. Install as a package (recommended):
   ```sh
   pip install .
   # or for development
   pip install -e .
   ```
   Or install dependencies manually:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

After installation, run the CLI with:
```sh
blitzcode --help
```
Or, if running directly:
```sh
python CLI_coder.py --help
```

### Main Commands

- **Interactive Agent Loop (with model selection):**
  ```sh
  blitzcode agent --model <model_name> [--groq-api-key <your_groq_api_key>]
  ```
  - Supported models: qwen-qwq-32b, llama-3.3-70b-versatile, deepseek-r1-distill-llama-70b, etc.
  - If using a Groq model, provide your API key via `--groq-api-key` or the `GROQ_API_KEY` environment variable.

- **Semantic Memory Agent (recommended for advanced workflows):**
  ```sh
  blitzcode semantic-agent
  ```
  - This launches the advanced agent with semantic memory, human-in-the-loop approval, and context-aware reasoning.
  - Type your queries at the prompt. Type `bye` or `exit` to quit.
  - To search your semantic memory, type:
    ```
    search: <your search query>
    ```

- **Inspect a file:**
  ```sh
  blitzcode inspect path/to/file.py
  ```

- **Scaffold a project:**
  ```sh
  blitzcode scaffold fastapi "ecommerce api"
  ```

### Model Initialization and API Keys
- **Groq Models:**
    - You must provide your own API key for Groq models. The CLI supports both the `--groq-api-key` argument and the `GROQ_API_KEY` environment variable.
    - Example:
      ```sh
      blitzcode agent --model qwen-qwq-32b --groq-api-key <your_groq_api_key>
      # or
      export GROQ_API_KEY=<your_groq_api_key>
      blitzcode agent --model qwen-qwq-32b
      ```
    - If neither is provided, the CLI will print an error and exit.
- **Gemini Model:**
    - Set your `GOOGLE_API_KEY` in the environment.
      ```sh
      export GOOGLE_API_KEY=<your_google_api_key>
      blitzcode agent --model gemini-2.0-flash
      ```
- **Other Models:**
    - See the CLI help for supported models and required keys.

## Example: Semantic Agent Session
```
$ blitzcode semantic-agent

Starting session for user: 123e4567-e89b-12d3-a456-426614174000

Enter your query : Scaffold a FastAPI project for a todo app
BlitzCoder: ... (AI response)

Enter your query : search: todo
Found 2 relevant memories for query: 'todo'
...
```

## API Key Notice
**You must provide your own API keys for Groq and Gemini models.**
- For Groq, use the `--groq-api-key` argument or set the `GROQ_API_KEY` environment variable.
- For Gemini, set the `GOOGLE_API_KEY` environment variable.
- Never share your API keys publicly.

## Demo Video

[![Watch the demo](demo.png)](demo.mp4)

> **Video Placeholder:**
> - Place your demo video as `demo.mp4` in this directory.
> - Add a thumbnail image as `demo.png` if desired.

## Description
Blitzcode CLI is designed for developers who want to:
- Rapidly scaffold and generate code projects using AI
- Interactively query, refactor, and explain code
- Automate repetitive coding and project setup tasks
- Keep sensitive files safe with .agentignore
- Enjoy a modern, colorized CLI experience

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](../LICENSE) 
