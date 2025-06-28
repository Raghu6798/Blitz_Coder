import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "README.md")
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = ""


setup(
    name="blitzcoder",
    version="1.0.0",
    description="AI-powered development assistant for code generation, refactoring, and project management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="BlitzCoder Team",
    author_email="raghunandanerukulla@gmail.com",
    url="https://github.com/Raghu6798/Blitz_Coder",
    packages=find_packages(where="src") + find_packages(where="."),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "python-dotenv>=0.0.1",
        "langgraph>=0.4.9",
        "langchain-groq>=0.3.4",
        "langchain-sambanova>=0.1.5",
        "langchain-google-genai>=2.1.5",
        "langchain>=0.3.26",
        "loguru>=0.7.3",
        "click>=8.1.8",
        "click-help-colors>=0.9.4",
        "rich>=14.0.0",
        "langfuse>=3.0.5",
    ],
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "blitzcoder=blitzcoder.cli.cli_coder:cli",
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Code Generators",
    ],
    keywords="ai, code-generation, development, assistant, cli",
    project_urls={
        "Bug Reports": "https://github.com/Raghu6798/Blitz_Coder/issues",
        "Source": "https://github.com/Raghu6798/Blitz_Coder",
    },
)
