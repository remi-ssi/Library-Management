@echo off
REM Library Management System Launcher for Windows
REM This batch file sets up the environment and launches the application

echo Starting Library Management System...

REM Get the directory where this batch file is located and go up one level to project root
set "SCRIPT_DIR=%~dp0"
for %%i in ("%SCRIPT_DIR%..") do set "PROJECT_DIR=%%~fi"

REM Create bin directory if it doesn't exist
if not exist "%PROJECT_DIR%\bin" mkdir "%PROJECT_DIR%\bin"

REM Create cache directory inside bin
if not exist "%PROJECT_DIR%\bin\cache" mkdir "%PROJECT_DIR%\bin\cache"

REM Set environment variable to redirect Python cache to bin folder
set "PYTHONPYCACHEPREFIX=%PROJECT_DIR%\bin\cache"

echo Python cache directory set to: %PYTHONPYCACHEPREFIX%

REM Change to project directory
cd /d "%PROJECT_DIR%"

REM First, clean any existing cache files in the working directory
echo Cleaning existing cache files...
for /d /r . %%d in (*__pycache__*) do (
    if not "%%d"=="%PROJECT_DIR%\bin\cache" (
        echo Removing %%d
        rmdir /s /q "%%d" 2>nul
    )
)

REM Launch the Authentication module directly with proper environment
echo Launching application...
python -c "
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '.')

try:
    from Authentication import Authentication, QApplication, QFont
    from navbar_logic import nav_manager
    
    app = QApplication(sys.argv)
    default_font = QFont('Times New Roman')
    app.setFont(default_font)
    app.setStyleSheet('QLabel {color: #4A4947}')
    
    window = Authentication()
    nav_manager.initialize(app)
    window.show()
    
    print('✅ Application started successfully!')
    sys.exit(app.exec())
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

pause
