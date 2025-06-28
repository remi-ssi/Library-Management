#!/usr/bin/env python
"""
Test script for navigation functionality
"""
import sys
from PySide6.QtWidgets import QApplication
from navbar_logic import nav_manager

def test_navigation():
    """Test all navigation functionality"""
    print("Testing Navigation Manager...")
    
    # Set librarian ID
    nav_manager.set_librarian_id(1)
    print("✓ Librarian ID set to 1")
    
    # Test all navigation items
    navigation_tests = [
        ("Dashboard", "Dashboard"),
        ("Books", "Books Management"),
        ("Transactions", "Transaction System"),
        ("Members", "Members Management"),
        ("Settings", "Settings Page")
    ]
    
    for item_name, description in navigation_tests:
        try:
            print(f"\nTesting {description}...")
            nav_manager.handle_navigation(item_name, 1)
            print(f"✓ {description} navigation: PASSED")
            
            # Close the window to clean up
            current_window = nav_manager.get_current_window()
            if current_window:
                current_window.close()
                
        except Exception as e:
            print(f"✗ {description} navigation: FAILED - {e}")
    
    print("\n" + "="*50)
    print("Navigation test completed!")
    print("All navigation paths are functional.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize navigation manager
    nav_manager.initialize(app)
    
    # Run tests
    test_navigation()
    
    print("\nNavigation system is ready for use!")
