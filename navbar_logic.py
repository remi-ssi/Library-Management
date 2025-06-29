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
        print(f"🧭 Navigation requested: {item_name} (librarian_id: {librarian_id})")
        
        if librarian_id is not None:
            self._librarian_id = librarian_id
            print(f"📝 Updated librarian_id to: {self._librarian_id}")
        
        # Hide current window if it exists
        if self._current_window:
            print(f"🔄 Closing current window: {type(self._current_window).__name__}")
            self._current_window.close()
            self._current_window = None
        
        try:
            # Handle navigation based on clicked item
            if item_name == "Dashboard":
                print("📊 Loading Dashboard...")
                from Dashboard import LibraryDashboard
                self._current_window = LibraryDashboard(librarian_id = self._librarian_id)
                
            elif item_name == "Books":
                print("📚 Loading Books...")
                from booksPages.books1 import CollapsibleSidebar
                self._current_window = CollapsibleSidebar(librarian_id=self._librarian_id)
                
            elif item_name == "Transactions":
                print("💰 Loading Transactions...")
                from transactionPages.Transaction1 import LibraryTransactionSystem
                self._current_window = LibraryTransactionSystem(librarian_id= self._librarian_id)
                
            elif item_name == "Members":
                print("👥 Loading Members...")
                from membersPages.members import MembersMainWindow
                self._current_window = MembersMainWindow(librarian_id=self._librarian_id)
               
            elif item_name == "Settings":
                print("⚙️ Loading Settings...")
                from librarianPages.settings import Settings
                self._current_window = Settings(librarian_id = self._librarian_id)
                
            else:
                print(f"❌ Unknown navigation item: {item_name}")
                return
                
            # Show the new window if one was created
            if self._current_window:
                print(f"✅ Showing window: {type(self._current_window).__name__}")
                self._current_window.show()
            else:
                print(f"❌ Failed to create window for: {item_name}")
                
        except ImportError as e:
            print(f"❌ Import error for {item_name}: {e}")
            # You could show a QMessageBox here if needed
        except Exception as e:
            print(f"❌ Error loading {item_name}: {e}")
            import traceback
            traceback.print_exc()

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