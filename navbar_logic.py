from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import QObject

class NavigationManager(QObject):
    def __init__(self):
        super().__init__()
        self._current_window = None
        self._librarian_id = None
    
    def initialize(self, app):
        """Initialize with QApplication instance"""
        self._app = app
    
    def set_librarian_id (self, librarian_id):
        self._librarian_id = librarian_id

    def handle_navigation(self, item_name, librarian_id=None):
        """Central navigation logic for all forms"""
        if librarian_id is not None:
            self._librarian_id = librarian_id
        # Hide current window if it exists
        if self._current_window:
            self._current_window.close()
            self._current_window = None
        
        # Handle navigation based on clicked item
        if item_name == "Dashboard":
            from Dashboard import LibraryDashboard
            self._current_window = LibraryDashboard(librarian_id = self._librarian_id)
            
        elif item_name == "Books":
            from books.books1 import CollapsibleSidebar
            self._current_window = CollapsibleSidebar(librarian_id=self._librarian_id)
            
        elif item_name == "Transactions":
            from transaction.Transaction1 import LibraryTransactionSystem
            self._current_window = LibraryTransactionSystem(librarian_id= self._librarian_id)
            
        elif item_name == "Members":
            from members.members import MembersMainWindow
            self._current_window = MembersMainWindow(librarian_id=self._librarian_id)
           
        elif item_name == "Settings":
            from librarian.settings import Settings
            self._current_window = Settings(librarian_id = self._librarian_id)
            
        # Show the new window if one was created
        if self._current_window:
            self._current_window.show()

    def get_current_window(self):
        """Return the currently active window"""
        return self._current_window
    
    def close_current_window(self):
        """Close the current window if it exists"""
        if self._current_window:
            self._current_window.close()
            self._current_window = None

# Create a single instance to be used across the application
nav_manager = NavigationManager()