# Environment Configuration

This folder contains all the environment setup and configuration files for the Library Management System.

## Files

### Setup Scripts
- **`setup_env.py`** - Main Python environment setup script
  - Configures Python cache directories
  - Sets environment variables
  - Provides usage instructions
  
- **`setup_env.bat`** - Windows batch file for easy setup
  - Double-click to run on Windows
  - Sets up environment automatically
  - User-friendly interface

### Configuration Files
- **`python_config.py`** - Python configuration module
  - Controls cache file locations
  - Sets PYTHONDONTWRITEBYTECODE
  - Manages import paths

### Testing
- **`test_bin_setup.py`** - Verification script
  - Tests that working directories are clean
  - Verifies bin folder organization
  - Validates environment setup

## Usage

### Quick Setup (Windows)
```bash
# Double-click this file or run:
setup_env.bat
```

### Manual Setup (Any OS)
```bash
# Run the Python setup script:
python "for environment config/setup_env.py"
```

### Verification
```bash
# Test that everything is working:
python "for environment config/test_bin_setup.py"
```

## Purpose

These files ensure that:
- ✅ Working directories stay clean (no `__pycache__` folders)
- ✅ Cache files are organized in the `bin/` folder
- ✅ Environment is properly configured for development
- ✅ Setup process is automated and user-friendly

## Project Structure

After setup, your project will have this clean structure:

```
LibraryManagement/
├── booksPages/                    # Clean source code
├── transactionPages/              # Clean source code  
├── membersPages/                  # Clean source code
├── librarianPages/                # Clean source code
├── bin/                          # All cache files here
├── for environment config/        # This folder
└── [other source files]          # Clean source code
```
