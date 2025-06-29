#!/usr/bin/env python3
"""
Environment Setup Script for Library Management System
This script configures the Python environment to keep all cache files in the bin folder
"""

import os
import sys
import shutil
from pathlib import Path

def clean_existing_cache():
    """Clean any existing __pycache__ folders from the working directory"""
    project_root = Path(__file__).parent.parent
    
    print("🧹 Cleaning existing cache files...")
    
    # Find and remove all __pycache__ directories
    cache_dirs = list(project_root.rglob("__pycache__"))
    
    for cache_dir in cache_dirs:
        # Skip if it's inside the bin folder (we want to keep those)
        if "bin" not in str(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"   ✅ Removed: {cache_dir}")
            except Exception as e:
                print(f"   ❌ Failed to remove {cache_dir}: {e}")
    
    # Also clean individual .pyc files
    pyc_files = list(project_root.rglob("*.pyc"))
    for pyc_file in pyc_files:
        if "bin" not in str(pyc_file):
            try:
                pyc_file.unlink()
                print(f"   ✅ Removed: {pyc_file}")
            except Exception as e:
                print(f"   ❌ Failed to remove {pyc_file}: {e}")

def setup_bin_directory():
    """Setup the bin directory structure"""
    project_root = Path(__file__).parent.parent
    bin_dir = project_root / "bin"
    cache_dir = bin_dir / "cache"
    
    print("📁 Setting up bin directory structure...")
    
    # Create directories
    bin_dir.mkdir(exist_ok=True)
    cache_dir.mkdir(exist_ok=True)
    
    print(f"   ✅ Created: {bin_dir}")
    print(f"   ✅ Created: {cache_dir}")
    
    return cache_dir

def create_env_files():
    """Create environment configuration files"""
    project_root = Path(__file__).parent.parent
    cache_dir = setup_bin_directory()
    
    print("📝 Creating environment configuration files...")
    
    # Create .env file for environment variables
    env_file = project_root / ".env"
    with open(env_file, "w") as f:
        f.write(f"# Library Management System Environment Configuration\n")
        f.write(f"PYTHONPYCACHEPREFIX={cache_dir}\n")
        f.write(f"PYTHONDONTWRITEBYTECODE=0\n")
        f.write(f"# Set to 1 to disable .pyc file generation entirely\n")
    
    print(f"   ✅ Created: {env_file}")
    
    # Create PowerShell script to set environment
    ps_script = project_root / "set_env.ps1"
    with open(ps_script, "w") as f:
        f.write(f"# PowerShell script to set environment variables\n")
        f.write(f"$env:PYTHONPYCACHEPREFIX = '{cache_dir}'\n")
        f.write(f"Write-Host 'Environment configured for Library Management System'\n")
        f.write(f"Write-Host 'Python cache directory: {cache_dir}'\n")
    
    print(f"   ✅ Created: {ps_script}")

def update_gitignore():
    """Ensure .gitignore is properly configured"""
    project_root = Path(__file__).parent.parent
    gitignore_file = project_root / ".gitignore"
    
    print("📝 Updating .gitignore...")
    
    # Read existing content
    existing_content = ""
    if gitignore_file.exists():
        with open(gitignore_file, "r") as f:
            existing_content = f.read()
    
    # Add cache-related entries if not present
    cache_entries = [
        "# Python cache files",
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        "",
        "# Bin folder for cache and compiled files",
        "bin/",
        "bin/*",
        "bin/**/*",
        "",
        "# Environment files",
        ".env",
        "set_env.ps1",
    ]
    
    # Check if we need to add anything
    needs_update = False
    for entry in cache_entries:
        if entry and entry not in existing_content:
            needs_update = True
            break
    
    if needs_update:
        with open(gitignore_file, "w") as f:
            f.write(existing_content)
            if not existing_content.endswith("\n"):
                f.write("\n")
            f.write("\n# Cache redirection entries\n")
            for entry in cache_entries:
                f.write(f"{entry}\n")
        print(f"   ✅ Updated: {gitignore_file}")
    else:
        print(f"   ✅ Already configured: {gitignore_file}")

def main():
    """Main setup function"""
    print("🚀 Setting up Library Management System environment...\n")
    
    try:
        clean_existing_cache()
        print()
        
        setup_bin_directory()
        print()
        
        create_env_files()
        print()
        
        update_gitignore()
        print()
        
        print("✅ Environment setup complete!")
        print("\n📋 To run the application with proper cache management:")
        print("   Windows: python run_app.py")
        print("   Or use:  run_app.bat")
        print("\n💡 All Python cache files will now be stored in the bin/cache folder")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
