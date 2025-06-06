from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QSizePolicy, QSpacerItem
)

class HoverButton(QPushButton):
    """Custom button that triggers sidebar expansion on hover"""
    def __init__(self, parent_sidebar):
        super().__init__()
        self.parent_sidebar = parent_sidebar
    
    def enterEvent(self, event):
        """Called when mouse enters the button"""
        self.parent_sidebar.expand_sidebar() #to trigger sidebar
        super().enterEvent(event) #call the event

class NavigationArea(QWidget):
    """Navigation area that detects mouse enter/leave events"""
    def __init__(self, parent_sidebar):
        super().__init__()
        self.parent_sidebar = parent_sidebar
        self.setMouseTracking(True)  # Enable mouse tracking
    
    def enterEvent(self, event):
        """Called when mouse enters the navigation area"""
        self.parent_sidebar.expand_sidebar()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Called when mouse leaves the navigation area"""
        self.parent_sidebar.start_collapse_timer()
        super().leaveEvent(event)

class NavigationSidebar(QWidget):
    """Collapsible navigation sidebar with hover animations"""
    
    def __init__(self, navigation_items=None):
        super().__init__()
        
        # Default navigation items if none provided
        if navigation_items is None:
            navigation_items = [
                ("assets/dashboard.png", "    Dashboard"),
                ("assets/books.png", "    Books"),
                ("assets/members.png", "    Members"),
                ("assets/settings.png", "    Settings")
            ]
        
        self.navigation_items = navigation_items
        self.init_sidebar()
        
    def init_sidebar(self):
        """Initialize the sidebar UI"""
        # Set fixed width for collapsed state
        self.setFixedWidth(60)
        self.setStyleSheet(
            """
            NavigationSidebar {
                background-color: #5c4033;
                border-radius: 10px;
            }
            """
        )
        
        # Main sidebar layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # Toggle button at the top
        self.toggle_button = QPushButton("< >")
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.toggle_button.setFixedHeight(40)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                color: #5C4033;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        self.main_layout.addWidget(self.toggle_button, alignment=Qt.AlignTop)

        # Spacer above icons (top empty space)
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Create navigation area widget that will detect mouse enter/leave
        self.nav_area = NavigationArea(self)
        self.nav_area.setStyleSheet("background-color: transparent;")
        
        # Navigation buttons layout (centered) - now inside nav_area
        self.nav_layout = QVBoxLayout(self.nav_area)
        self.nav_layout.setAlignment(Qt.AlignTop)
        self.nav_layout.setContentsMargins(5, 10, 5, 10)  # Add some padding

        self.buttons = []
        self.create_navigation_buttons()

        # Add the navigation area to the main sidebar layout
        self.main_layout.addWidget(self.nav_area)

        # Spacer below icons (bottom empty space)
        self.main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Animation and state setup
        self.setup_animations()
        
    def create_navigation_buttons(self):
        """Create navigation buttons from the provided items"""
        for icon_path, label in self.navigation_items:
            btn = HoverButton(self)  # Use custom HoverButton
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(30, 30))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setMinimumHeight(40)
            btn.label_text = label
            btn.setText("")  # Start with no text

            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 10px;
                    color: #5C4033;
                    border: none;
                    font-size: 18px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """)

            btn.setLayoutDirection(Qt.LeftToRight)
            
            # Connect button click to callback
            btn.clicked.connect(lambda checked, text=label.strip(): self.on_navigation_clicked(text))
            
            self.nav_layout.addWidget(btn)
            self.buttons.append(btn)
    
    def setup_animations(self):
        """Setup animation properties and timers"""
        # Animation state variables
        self.expanded = False
        self.manually_expanded = False  # Track if expanded by toggle button
        
        # Animation setup
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(250)
        
        # Timer for delayed collapse (prevents flickering when moving mouse quickly)
        self.collapse_timer = QTimer()
        self.collapse_timer.setSingleShot(True)
        self.collapse_timer.timeout.connect(self.collapse_sidebar_hover)

    def toggle_sidebar(self):
        """Manual toggle function using the <> button"""
        self.manually_expanded = not self.manually_expanded
        self.collapse_timer.stop()
        
        if self.manually_expanded:
            self.expand_sidebar_manual()
        else:
            self.collapse_sidebar_manual()

    def expand_sidebar_manual(self):
        """Expand the sidebar manually (via toggle button)"""
        self.expanded = True
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(180)
        for btn in self.buttons:
            btn.setText(f"  {btn.label_text}")
        self.animation.start()

    def collapse_sidebar_manual(self):
        """Collapse the sidebar manually (via toggle button)"""
        self.expanded = False
        self.animation.setStartValue(self.width())
        self.animation.setEndValue(60)
        for btn in self.buttons:
            btn.setText("")
        self.animation.start()

    def expand_sidebar(self):
        """Expand the sidebar on hover (only if not manually expanded)"""
        if not self.manually_expanded and not self.expanded:
            self.expanded = True
            self.collapse_timer.stop()
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(180)
            for btn in self.buttons:
                btn.setText(f"  {btn.label_text}")
            self.animation.start()

    def start_collapse_timer(self):
        """Start the collapse timer (only if not manually expanded)"""
        if not self.manually_expanded:
            self.collapse_timer.start(200)

    def collapse_sidebar_hover(self):
        """Collapse the sidebar on hover timeout (only if not manually expanded)"""
        if not self.manually_expanded and self.expanded:
            self.expanded = False
            self.animation.setStartValue(self.width())
            self.animation.setEndValue(60)
            for btn in self.buttons:
                btn.setText("")
            self.animation.start()
    
    def on_navigation_clicked(self, item_name):
        """Handle navigation button clicks - override this method"""
        print(f"Navigation clicked: {item_name}")
        # Override this method in your main application to handle navigation
        pass
    
    def set_navigation_items(self, navigation_items):
        """Update navigation items dynamically"""
        # Clear existing buttons
        for btn in self.buttons:
            btn.setParent(None)
        self.buttons.clear()
        
        # Set new items and recreate buttons
        self.navigation_items = navigation_items
        self.create_navigation_buttons()
    
    def get_current_state(self):
        """Get current sidebar state"""
        return {
            'expanded': self.expanded,
            'manually_expanded': self.manually_expanded,
            'width': self.width()
        }

# Example usage and testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QLabel
    from PySide6.QtGui import QFont
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Navigation Sidebar Test")
            self.setFixedSize(800, 600)
            
            # Create main widget
            main_widget = QWidget()
            self.setCentralWidget(main_widget)
            
            # Create layout
            layout = QHBoxLayout(main_widget)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Create custom navigation sidebar
            custom_nav_items = [
                ("assets/dashboard.png", "    Dashboard"),
                ("assets/books.png", "    Books"),
                ("assets/members.png", "    Members"),
                ("assets/settings.png", "    Settings"),
                ("assets/reports.png", "    Reports")
            ]
            
            self.sidebar = NavigationSidebar(custom_nav_items)
            # Override the navigation click handler
            self.sidebar.on_navigation_clicked = self.handle_navigation
            
            # Create content area
            content_area = QWidget()
            content_area.setStyleSheet("background-color: #f1efe3;")
            self.content_label = QLabel("Main Content Area\nClick navigation items to test")
            self.content_label.setAlignment(Qt.AlignCenter)
            self.content_label.setStyleSheet("""
                QLabel {
                    color: #5C4033;
                    font-size: 24px;
                    font-weight: bold;
                }
            """)
            
            content_layout = QVBoxLayout(content_area)
            content_layout.addWidget(self.content_label)
            
            # Add to main layout
            layout.addWidget(self.sidebar)
            layout.addWidget(content_area)
        
        def handle_navigation(self, item_name):
            """Handle navigation clicks"""
            self.content_label.setText(f"Selected: {item_name}\n\nSidebar working correctly!")
            print(f"Navigation clicked: {item_name}")
    
    app = QApplication(sys.argv)
    app.setFont(QFont("Times New Roman", 10))
    window = TestWindow()
    window.show()
    sys.exit(app.exec())