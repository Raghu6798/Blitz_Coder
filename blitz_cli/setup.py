import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, "..", "README.md")
try:
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()
except Exception:
    long_description = ""


setup(
    name="blitzcode",
    version="0.1.0",
    description="AI-powered code agent and utilities for developers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Raghu Nandan Erukulla",
    author_email="raghunandanerukulla@gmail.com",
    url="https://github.com/Raghu6798/BlitzCoder",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "python-dotenv>=0.0.1",
        "langgraph>=0.4.9",
        "langchain-groq>=0.3.4",
        "langchain-sambanova>=0.1.5",
         "langchain-google-genai>=2.1.5",
        "langchain>=0.3.26",
        "loguru>=0.7.3",
        "langchain-google-genai>=2.1.5",
        "click>=8.1.8",
        "click-help-colors>=0.9.4",
        "rich>=14.0.0",
        "langfuse>=3.0.5",
    ],
    python_requires=">=3.9",
    entry_points={"console_scripts": ["blitzcode=blitz_cli.src.blitzcoder.cli.CLI_coder"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
