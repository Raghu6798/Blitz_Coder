#!/usr/bin/env python3
"""
BlitzCoder Installation Script

This script installs the BlitzCoder package in development mode.
"""

import subprocess
import sys
import os

def install_package():
    """Install the package in development mode"""
    try:
        print("Installing BlitzCoder in development mode...")
        
        # Install in development mode
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-e", "."
        ], cwd=os.path.dirname(os.path.abspath(__file__)))
        
        print("✅ BlitzCoder installed successfully!")
        print("\nYou can now use the CLI with:")
        print("  blitzcoder --help")
        print("  blitzcoder chat")
        print("  blitzcoder search-memories")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Installation failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_package() 