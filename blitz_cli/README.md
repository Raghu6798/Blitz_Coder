# BlitzCode CLI

> **AI-powered code agent and utilities for developers**

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

### Option 1: Install as a Python Package (Recommended)

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Blitzcode/blitz_cli
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Test the installation:
```bash
blitzcode --help
```

### Option 2: Run Directly

```bash
python -m src.blitzcoder.cli.CLI_coder interactive --google-api-key YOUR_API_KEY
```

## Usage

### Interactive Mode

Start the interactive AI agent:

```bash
# With API key as argument
blitzcode interactive --google-api-key YOUR_API_KEY

# Or let it prompt you for the API key
blitzcode interactive
```

### Search Memories

Search through your conversation history:

```bash
blitzcode search-memories-cli --query "your search query" --google-api-key YOUR_API_KEY
```

### Available Commands

- `blitzcode interactive` - Start interactive AI agent
- `blitzcode search-memories-cli` - Search conversation memories
- `blitzcode --help` - Show all available commands

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
