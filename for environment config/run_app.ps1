# Library Management System Launcher for PowerShell
# This script sets up the environment and launches the application

Write-Host "Starting Library Management System..." -ForegroundColor Green

# Get the directory where this script is located and go up one level to project root
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$PROJECT_DIR = Split-Path -Parent $SCRIPT_DIR

# Create bin directory if it doesn't exist
$BIN_DIR = Join-Path $PROJECT_DIR "bin"
$CACHE_DIR = Join-Path $BIN_DIR "cache"

if (!(Test-Path $BIN_DIR)) {
    New-Item -ItemType Directory -Path $BIN_DIR -Force | Out-Null
}

if (!(Test-Path $CACHE_DIR)) {
    New-Item -ItemType Directory -Path $CACHE_DIR -Force | Out-Null
}

# Set environment variable to redirect Python cache to bin folder
$env:PYTHONPYCACHEPREFIX = $CACHE_DIR

Write-Host "Python cache directory set to: $($env:PYTHONPYCACHEPREFIX)" -ForegroundColor Yellow

# Change to project directory
Set-Location $PROJECT_DIR

# Clean any existing cache files in the working directory
Write-Host "Cleaning existing cache files..." -ForegroundColor Blue
Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__" | ForEach-Object {
    $fullPath = Join-Path $PROJECT_DIR $_
    if ($fullPath -ne $CACHE_DIR) {
        Write-Host "Removing $fullPath"
        Remove-Item -Path $fullPath -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Launch the application
Write-Host "Launching application..." -ForegroundColor Green

$pythonCode = @"
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
"@

python -c $pythonCode

Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
