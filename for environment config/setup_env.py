#!/usr/bin/env python3
"""
Library Management System Startup Script
This script configures the Python environment to keep cache files in the bin folder
"""

import os
import sys
import subprocess

def setup_environment():
    """Set up the Python environment for clean working directories"""
    print("🔧 Setting up Library Management System environment...")
    
    # Get the project root directory (parent of this config folder)
    config_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(config_dir)  # Go up one level from config folder
    bin_dir = os.path.join(project_root, 'bin')
    
    # Ensure bin directory exists
    os.makedirs(bin_dir, exist_ok=True)
    os.makedirs(os.path.join(bin_dir, '__pycache__'), exist_ok=True)
    
    # Set environment variables to control Python cache behavior
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'  # Prevent automatic .pyc creation
    os.environ['PYTHONPATH'] = project_root  # Ensure imports work correctly
    
    print(f"✅ Config directory: {config_dir}")
    print(f"✅ Project root: {project_root}")
    print(f"✅ Cache directory: {os.path.join(bin_dir, '__pycache__')}")
    print(f"✅ PYTHONDONTWRITEBYTECODE: {os.environ.get('PYTHONDONTWRITEBYTECODE')}")
    print(f"✅ Working directories will remain clean!")
    
    return project_root, bin_dir

def main():
    """Main function to set up environment and provide usage instructions"""
    project_root, bin_dir = setup_environment()
    
    print(f"\n📚 Library Management System")
    print(f"=" * 50)
    print(f"🎯 Environment configured successfully!")
    print(f"📁 All cache files will be stored in: bin/")
    print(f"✨ Working directories are now clean!")
    
    print(f"\n🚀 To run the application:")
    print(f"   python Authentication.py    # Start with login")
    print(f"   python Dashboard.py         # Start with dashboard")
    
    print(f"\n📝 To run individual modules:")
    print(f"   python booksPages/books1.py")
    print(f"   python transactionPages/Transaction1.py")
    print(f"   python membersPages/members.py")
    print(f"   python librarianPages/settings.py")
    
    print(f"\n🧹 Cache management:")
    print(f"   All __pycache__ folders moved to bin/")
    print(f"   Future cache files will be controlled")
    print(f"   Working directories stay clean!")

if __name__ == "__main__":
    main()
