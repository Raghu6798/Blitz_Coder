@echo off
REM BlitzCoder CLI Entry Point for Windows

REM Get the directory where this batch file is located
set SCRIPT_DIR=%~dp0

REM Add the src directory to the Python path and run the CLI
python "%SCRIPT_DIR%..\src\blitzcoder\cli\cli_coder.py" %* 