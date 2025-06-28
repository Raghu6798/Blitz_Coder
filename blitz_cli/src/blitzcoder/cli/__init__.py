"""
BlitzCoder CLI - AI-Powered Development Assistant

A command-line interface for AI-powered code generation, refactoring, and project management.
"""

from .cli_coder import cli, run_agent_with_memory, search_memories_cli

__version__ = "1.0.0"
__author__ = "BlitzCoder Team"
__description__ = "AI-Powered Development Assistant CLI"

__all__ = [
    "cli",
    "run_agent_with_memory", 
    "search_memories_cli"
]
