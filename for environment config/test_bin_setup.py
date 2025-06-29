#!/usr/bin/env python3
"""
Test script to verify that bin folder setup is working correctly
"""

import os
import sys

def test_clean_directories():
    """Test that working directories are clean of __pycache__"""
    print("🧪 Testing clean directory setup...")
    
    # Define working directories to check
    working_dirs = [
        "booksPages",
        "transactionPages", 
        "membersPages",
        "librarianPages"
    ]
    
    # Get project root (parent of this config folder)
    config_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(config_dir)
    all_clean = True
    
    for dir_name in working_dirs:
        dir_path = os.path.join(project_root, dir_name)
        if os.path.exists(dir_path):
            pycache_path = os.path.join(dir_path, "__pycache__")
            if os.path.exists(pycache_path):
                print(f"❌ Found __pycache__ in {dir_name}")
                all_clean = False
            else:
                print(f"✅ {dir_name} is clean")
        else:
            print(f"⚠️ Directory {dir_name} not found")
    
    # Check main directory
    main_pycache = os.path.join(project_root, "__pycache__")
    if os.path.exists(main_pycache):
        print(f"❌ Found __pycache__ in main directory")
        all_clean = False
    else:
        print(f"✅ Main directory is clean")
    
    return all_clean

def test_bin_folder():
    """Test that bin folder contains the moved cache files"""
    print(f"\n🧪 Testing bin folder setup...")
    
    # Get project root (parent of this config folder)
    config_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(config_dir)
    bin_path = os.path.join(project_root, "bin")
    
    if not os.path.exists(bin_path):
        print(f"❌ Bin folder not found")
        return False
    
    print(f"✅ Bin folder exists")
    
    # Check for moved cache directories
    expected_cache_dirs = [
        "main_pycache",
        "booksPages_pycache",
        "transactionPages_pycache",
        "membersPages_pycache", 
        "librarianPages_pycache"
    ]
    
    found_dirs = 0
    for cache_dir in expected_cache_dirs:
        cache_path = os.path.join(bin_path, cache_dir)
        if os.path.exists(cache_path):
            print(f"✅ Found {cache_dir}")
            found_dirs += 1
        else:
            print(f"⚠️ {cache_dir} not found")
    
    print(f"📊 Found {found_dirs}/{len(expected_cache_dirs)} expected cache directories")
    
    # Check README
    readme_path = os.path.join(bin_path, "README.md")
    if os.path.exists(readme_path):
        print(f"✅ README.md found in bin folder")
    else:
        print(f"⚠️ README.md not found in bin folder")
    
    return found_dirs >= 3  # At least 3 cache directories should be present

def test_environment_setup():
    """Test environment setup"""
    print(f"\n🧪 Testing environment setup...")
    
    # Check if setup files exist in config folder
    config_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(config_dir)
    
    setup_files = {
        "setup_env.py": "Python setup script",
        "setup_env.bat": "Windows batch setup script",
        "python_config.py": "Python configuration file"
    }
    
    all_found = True
    for filename, description in setup_files.items():
        file_path = os.path.join(config_dir, filename)  # Files are in config dir
        if os.path.exists(file_path):
            print(f"✅ {description}: {filename}")
        else:
            print(f"❌ Missing {description}: {filename}")
            all_found = False
    
    return all_found

if __name__ == "__main__":
    print("🚀 Testing bin folder setup...\n")
    
    # Run tests
    clean_dirs = test_clean_directories()
    bin_setup = test_bin_folder()
    env_setup = test_environment_setup()
    
    print(f"\n📊 Test Results:")
    print(f"   Clean directories: {'✅ PASSED' if clean_dirs else '❌ FAILED'}")
    print(f"   Bin folder setup: {'✅ PASSED' if bin_setup else '❌ FAILED'}")
    print(f"   Environment setup: {'✅ PASSED' if env_setup else '❌ FAILED'}")
    
    if clean_dirs and bin_setup and env_setup:
        print(f"\n🎉 Bin folder setup SUCCESS!")
        print(f"✅ All working directories are clean")
        print(f"✅ Cache files are organized in bin/")
        print(f"✅ Environment setup files are ready")
        print(f"\n📁 Your project structure is now clean and organized!")
    else:
        print(f"\n❌ Some tests failed. Check the output above.")
        sys.exit(1)
