import sys
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                              QLineEdit, QFrame, QScrollArea, QStackedWidget,
                              QListWidget, QListWidgetItem, QSizePolicy)
from PySide6.QtCore import Qt, QTimer, QSize, Signal
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QIcon
from navigation_sidebar import NavigationSidebar  
from navbar_logic import nav_manager

class LibraryDashboard(QMainWindow):
    def __init__(self, librarian_id=None):
        super().__init__()
        self.librarian_id = librarian_id
        self.dark_mode = False
        self.init_ui()
        self.setup_timer()
        self.apply_styles()
        
    def init_ui(self):
        self.setWindowTitle("BJRS Library")
        self.setGeometry(100, 100, 1400, 900)
        self.showMaximized()
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.sidebar = NavigationSidebar()
        self.sidebar.on_navigation_clicked = lambda item_name: nav_manager.handle_navigation(item_name, self.librarian_id)
        main_layout.addWidget(self.sidebar)
        
        content_area = QWidget()
        content_area.setStyleSheet("background-color: #f1efe3;")
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        header = self.create_header()
        content_layout.addWidget(header)        
        stats = self.create_stats_section()
        content_layout.addWidget(stats)
        
        available_books = self.create_available_books_section()
        content_layout.addWidget(available_books)
        
        main_layout.addWidget(content_area)
        
    def create_header(self):
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(80)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 0, 20, 0)        
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(2)
        
        self.welcome_label = QLabel("Hello, Librarian!")
        self.welcome_label.setObjectName("welcomeTitle")
        
        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("dateTime")
        
        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.addWidget(self.datetime_label)        
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(12)        
        search_widget = QWidget()
        search_widget.setObjectName("searchWidget")
        search_widget.setFixedWidth(300)
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(8, 0, 8, 0)
        
        search_icon = QLabel("🔍")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search books, members...")
        self.search_input.setObjectName("searchInput")
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input)
        
        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setObjectName("themeButton")
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        actions_layout.addWidget(search_widget)
        actions_layout.addWidget(self.theme_btn)
        
        layout.addWidget(welcome_widget)
        layout.addStretch()
        layout.addWidget(actions_widget)
        
        return header
    
    def create_stats_section(self):
        stats_widget = QWidget()
        layout = QGridLayout(stats_widget)
        layout.setSpacing(20)
        
        stats_data = [
            ("📚", "1,847", "Total Books", "#22c55e"),
            ("👥", "342", "Active Members", "#d2691e"),
            ("📋", "128", "Books Issued", "#f59e0b"),
            ("⚠️", "23", "Overdue Books", "#ef4444")
        ]
        
        for i, (icon, number, label, color) in enumerate(stats_data):
            card = self.create_stat_card(icon, number, label, color)
            layout.addWidget(card, 0, i)
        
        return stats_widget
    
    def create_stat_card(self, icon, number, label, color):
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(120)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        
        header_layout = QHBoxLayout()
        
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(4)
        
        number_label = QLabel(number)
        number_label.setObjectName("statNumber")
        
        label_widget = QLabel(label)
        label_widget.setObjectName("statLabel")
        
        text_layout.addWidget(number_label)
        text_layout.addWidget(label_widget)
        
        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        icon_label.setFixedSize(48, 48)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"background-color: {color}; border-radius: 10px; font-size: 20px;")
        
        header_layout.addWidget(text_widget)
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        
        layout.addLayout(header_layout)
        layout.addStretch()
        
        return card
    
    def create_available_books_section(self):
        section = QFrame()
        section.setObjectName("sectionCard")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        title_label = QLabel("📖 Available Books")
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)
        
        books_area = QFrame()
        books_area.setObjectName("booksArea")
        books_area.setMinimumHeight(400)
        books_area.setStyleSheet("""
            QFrame#booksArea {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 8px;
            }        """)
        
        books_area_layout = QVBoxLayout(books_area)
        books_area_layout.setAlignment(Qt.AlignCenter)
        
        empty_label = QLabel("")
        empty_label.setAlignment(Qt.AlignCenter)
        books_area_layout.addWidget(empty_label)
        
        layout.addWidget(books_area)
        
        return section
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(60000)
        self.update_datetime()
    
    def update_datetime(self):
        now = datetime.now()
        formatted_time = now.strftime("%A, %B %d, %Y at %I:%M %p")
        self.datetime_label.setText(formatted_time)
    
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText("☀️" if self.dark_mode else "🌙")
        self.apply_styles()
    
    def apply_styles(self):
        if self.dark_mode:
            colors = {
                'dark_brown': '#5e3e1f',
                'light_brown': '#e8d8bd',
                'bg_color': '#2a1f16',
                'text_color': '#e8d8bd',
                'card_color': '#3d2a1a',
                'border_color': '#444'
            }
        else:
            colors = {
                'dark_brown': '#5e3e1f',
                'light_brown': '#e8d8bd',
                'bg_color': '#f8f5f1',
                'text_color': '#333',
                'card_color': '#ffffff',
                'border_color': '#ddd'
            }
        
        style = f"""
        QMainWindow {{
            background-color: {colors['bg_color']};
            color: {colors['text_color']};
        }}
        
        QFrame#headerFrame {{
            background-color: {colors['card_color']};
            border-radius: 12px;
        }}
        
        QLabel#welcomeTitle {{
            color: {colors['dark_brown']};
            font-size: 24px;
            font-weight: bold;
        }}
        
        QLabel#dateTime {{
            color: #666;
            font-size: 14px;
        }}
        
        QWidget#searchWidget {{
            background-color: {colors['bg_color']};
            border: 1px solid {colors['border_color']};
            border-radius: 8px;
            padding: 4px;
        }}
        
        QLineEdit#searchInput {{
            background-color: transparent;
            border: none;
            color: {colors['text_color']};
            font-size: 14px;
        }}
        
        QPushButton#themeButton {{
            background-color: {colors['dark_brown']};
            color: {colors['light_brown']};
            border: none;
            border-radius: 8px;
            font-size: 16px;
        }}
        
        QPushButton#themeButton:hover {{
            background-color: #d2691e;
        }}
        
        QFrame#statCard {{
            background-color: {colors['card_color']};
            border-radius: 12px;
            border-left: 4px solid {colors['dark_brown']};
        }}
        
        QLabel#statNumber {{
            color: {colors['dark_brown']};
            font-size: 28px;
            font-weight: bold;
        }}
        
        QLabel#statLabel {{
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
        }}
        
        QFrame#sectionCard {{
            background-color: {colors['card_color']};
            border-radius: 12px;
        }}
        
        QLabel#sectionTitle {{
            color: {colors['dark_brown']};
            font-size: 18px;
            font-weight: 600;
        }}
        
        QFrame#booksArea {{
            background-color: #f8f9fa;
            border: 2px dashed #dee2e6;
            border-radius: 8px;
        }}        """
        
        if self.dark_mode:
            style += f"""
            QLabel#welcomeTitle {{
                color: {colors['light_brown']};
            }}
            
            QLabel#dateTime {{
                color: #999;
            }}
            
            QLabel#statNumber {{
                color: {colors['light_brown']};
            }}
            
            QLabel#statLabel {{
                color: #999;
            }}
            
            QLabel#sectionTitle {{
                color: {colors['light_brown']};
            }}
            
            QFrame#booksArea {{
                background-color: rgba(232, 216, 189, 0.1);
                border: 2px dashed rgba(232, 216, 189, 0.3);
            }}
            """
        
        self.setStyleSheet(style)

def main():
    app = QApplication(sys.argv)
    
    nav_manager.initialize(app)
    window = LibraryDashboard()
    nav_manager._current_window = window
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
