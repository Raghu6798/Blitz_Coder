# Blitzcode CLI

**AI-powered code agent and utilities for developers**

![Blitzcode Banner](../assets/banner.png)

## Overview
Blitzcode CLI is a powerful, AI-driven command-line tool that helps you scaffold, generate, inspect, and manage code projects at terminal speed. It leverages advanced language models to automate repetitive coding tasks, provide code explanations, refactor code, and much more—all from your terminal.

## Features
- **AI-powered project scaffolding** for popular frameworks (FastAPI, Spring Boot, Next.js, etc.)
- **Code generation** for files, modules, and entire architectures
- **Interactive agent loop** with model selection (Qwen, Gemini, Llama, etc.)
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
2. Install dependencies (using uv, poetry, or pip):
   ```sh
   uv pip install -r requirements.txt
   # or
   poetry install
   # or
   pip install -r requirements.txt
   ```
3. (Optional) Install `click-help-colors` for colorized help:
   ```sh
   pip install click-help-colors
   ```

## Usage

Run the CLI with:
```sh
python CLI_coder.py --help
```

### Example Commands
- Inspect a file:
  ```sh
  python CLI_coder.py inspect path/to/file.py
  ```
- Scaffold a FastAPI project:
  ```sh
  python CLI_coder.py scaffold fastapi "ecommerce api"
  ```
- Start the interactive agent loop (with model selection):
  ```sh
  python CLI_coder.py agent --model gemini-2.0-flash
  ```

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
