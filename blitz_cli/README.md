# BlitzCoder

⚡ **AI-Powered Development Assistant** - A comprehensive CLI tool for code generation, refactoring, and project management.

## Features

- 🤖 **AI-Powered Code Generation** - Generate code using Google's Gemini model
- 🔧 **Code Refactoring** - Automatically refactor and improve existing code
- 📁 **Project Scaffolding** - Create complete project structures with architecture plans
- 🧠 **Memory System** - Remember previous conversations and context
- 🛠️ **Development Tools** - File inspection, execution, and management tools
- 🔍 **Code Analysis** - Explain and analyze code functionality

## Installation

### Option 1: Install from Source (Recommended)

```bash
# Clone the repository
git clone https://github.com/Raghu6798/Blitz_Coder.git
cd BlitzCoder/blitz_cli

# Install in development mode
python install.py
```

### Option 2: Manual Installation

```bash
cd blitz_cli
pip install -e .
```

### Option 3: Direct Script Execution

```bash
# Windows
python scripts/blitzcoder.bat

# Linux/Mac
python scripts/blitzcoder
```

## Quick Start

### 1. Set up your API Keys

You'll need a Google API key for the Gemini model:

```bash
# Set environment variable
export GOOGLE_API_KEY="your-api-key-here"

# Or on Windows
set GOOGLE_API_KEY=your-api-key-here
```

### 2. Start Interactive Chat

```bash
blitzcoder chat
```

### 3. Search Memories

```bash
blitzcoder search-memories --query "your search term"
```

## Usage Examples

### Interactive Chat Mode

```bash
blitzcoder chat
```

This starts an interactive session where you can:
- Ask questions about code
- Request code generation
- Get help with refactoring
- Search through previous conversations

### Search Previous Conversations

```bash
blitzcoder search-memories --query "React component"
```

### Use with API Key Parameter

```bash
blitzcoder chat --google-api-key "your-api-key"
```

## Available Commands

| Command | Description |
|---------|-------------|
| `chat` | Start interactive AI chat session |
| `search-memories` | Search through conversation history |

## Development

### Project Structure

```
blitz_cli/
├── src/
│   └── blitzcoder/
│       ├── cli/
│       │   ├── __init__.py
│       │   └── cli_coder.py
│       └── __init__.py
├── config/
│   └── templates/
├── scripts/
│   ├── blitzcoder
│   └── blitzcoder.bat
├── setup.py
├── pyproject.toml
└── install.py
```

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

### Code Formatting

```bash
# Format code
black src/
isort src/

# Type checking
mypy src/
```

## Configuration

The package uses environment variables for configuration:

- `GOOGLE_API_KEY` - Required for Gemini model access
- `GROQ_API_KEY` - Optional for additional models
- `NOVITA_API_KEY` - Optional for embeddings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- 📧 Email: raghunandanerukulla@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/Raghu6798/BlitzCoder/issues)
- 📖 Documentation: [GitHub README](https://github.com/Raghu6798/BlitzCoder#readme)

## Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph)
- Powered by [Google Gemini](https://ai.google.dev/)
- Enhanced with [Rich](https://github.com/Textualize/rich) for beautiful CLI output 
