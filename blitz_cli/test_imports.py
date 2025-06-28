#!/usr/bin/env python3
"""
Test script to check if imports work correctly
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    print("Testing imports...")
    
    # Test importing the main package
    from blitzcoder import cli
    print("✅ blitzcoder.cli imported successfully")
    
    # Test importing the CLI module
    from blitzcoder.cli import cli_coder
    print("✅ blitzcoder.cli.cli_coder imported successfully")
    
    # Test importing the CLI function
    from blitzcoder.cli.cli_coder import cli
    print("✅ cli function imported successfully")
    
    print("\n🎉 All imports successful!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc() 