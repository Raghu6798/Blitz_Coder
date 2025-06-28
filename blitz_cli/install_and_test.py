#!/usr/bin/env python3
"""
Installation and testing script for BlitzCode package
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 BlitzCode Package Installation and Testing")
    print("=" * 50)
    
    # Step 1: Install the package in development mode
    if not run_command("pip install -e .", "Installing BlitzCode package in development mode"):
        print("❌ Installation failed. Please check the error messages above.")
        return False
    
    # Step 2: Test if the command is available
    if not run_command("blitzcode --help", "Testing if blitzcode command is available"):
        print("❌ Command test failed. The package might not be installed correctly.")
        return False
    
    # Step 3: Test the interactive command help
    if not run_command("blitzcode interactive --help", "Testing interactive command help"):
        print("❌ Interactive command test failed.")
        return False
    
    print("\n🎉 All tests passed! Your BlitzCode package is ready to use.")
    print("\n📝 Usage examples:")
    print("  blitzcode interactive --google-api-key YOUR_API_KEY")
    print("  blitzcode search-memories-cli --query 'your search query' --google-api-key YOUR_API_KEY")
    print("  blitzcode --help")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 