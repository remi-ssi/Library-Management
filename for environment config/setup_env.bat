@echo off
REM Library Management System Environment Setup
REM This batch file sets up the environment and runs the setup script

echo 🔧 Setting up Library Management System...
echo.

REM Change to the project directory (parent of this config folder)
cd /d "%~dp0\.."

REM Set environment variables
set PYTHONDONTWRITEBYTECODE=1
set PYTHONPATH=%CD%

REM Run the Python setup script
python "for environment config\setup_env.py"

echo.
echo ✅ Environment setup complete!
echo 📁 All cache files will be stored in the bin/ folder
echo ✨ Your working directories are now clean!
echo.
pause
