#!/usr/bin/env python3
"""
Library Management System Launcher
This script sets up the environment to redirect all Python cache files to the bin folder
and then launches the Authentication module.
"""

import os
import sys
from pathlib import Path

def setup_cache_environment():
    """Set up environment to redirect Python cache to bin folder"""
    # Get the project root directory (parent of this script's directory)
    script_dir = Path(__file__).parent.absolute()
    project_dir = script_dir.parent  # Go up one level to project root
    bin_dir = project_dir / "bin"
    
    # Create bin directory if it doesn't exist
    bin_dir.mkdir(exist_ok=True)
    
    # Set PYTHONPYCACHEPREFIX to redirect cache files to bin folder
    cache_dir = bin_dir / "cache"
    cache_dir.mkdir(exist_ok=True)
    
    # Set environment variable (this affects future Python processes)
    os.environ['PYTHONPYCACHEPREFIX'] = str(cache_dir)
    
    # For the current process, we need to use a different approach
    # Since PYTHONPYCACHEPREFIX only works when set before Python starts,
    # we'll clean any existing cache and ensure future runs use the prefix
    
    print(f"✅ Python cache directory configured: {cache_dir}")
    print("ℹ️ Cache redirection will take effect on next Python restart")
    
    # Add project directory to Python path for imports
    sys.path.insert(0, str(project_dir))

def main():
    """Main function to launch the application"""
    print("🚀 Starting Library Management System...")
    
    # Setup environment
    setup_cache_environment()
    
    try:
        # Import and run the Authentication module
        from Authentication import Authentication, QApplication, QFont
        
        # Create the application
        app = QApplication(sys.argv)
        
        # Set default font
        default_font = QFont("Times New Roman")
        app.setFont(default_font)
        app.setStyleSheet("""
            QLabel {color: #4A4947}         
        """)
        
        # Create and show the authentication window
        window = Authentication()
        
        # Initialize navigation manager
        from navbar_logic import nav_manager
        nav_manager.initialize(app)
        
        window.show()
        
        print("✅ Application started successfully!")
        
        # Run the application
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
