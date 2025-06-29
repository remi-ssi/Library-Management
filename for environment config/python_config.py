# Python configuration for Library Management System
# This file sets up Python to use the bin folder for cache files

import os
import sys

# Set the cache directory to bin folder
CACHE_DIR = os.path.join(os.path.dirname(__file__), 'bin', '__pycache__')

# Create cache directory if it doesn't exist
os.makedirs(CACHE_DIR, exist_ok=True)

# Set PYTHONDONTWRITEBYTECODE to prevent automatic .pyc creation
# We'll handle cache manually when needed
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

print(f"📁 Python cache configured to use: {CACHE_DIR}")
