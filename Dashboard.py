import sys
from datetime import datetime, timedelta
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                              QLineEdit, QFrame, QScrollArea, QStackedWidget,
                              QListWidget, QListWidgetItem, QSizePolicy,
                              QTableWidget, QTableWidgetItem, QCheckBox, QHeaderView,
                              QAbstractItemView, QMessageBox)
from PySide6.QtCore import Qt, QTimer, QSize, Signal, QDate
from PySide6.QtGui import QFont, QPalette, QColor, QPixmap, QPainter, QIcon
from navigation_sidebar import NavigationSidebar  
from navbar_logic import nav_manager

class LibraryDashboard(QMainWindow):
    def __init__(self, librarian_id=None):  
        super().__init__()
        self.librarian_id = librarian_id  
        self.init_sample_data()
        self.init_ui()
        self.setup_timer()
        
    def init_sample_data(self):
        # SAMPLE DATA FOR DUE THIS WEEK ^_^
        today = datetime.now()
        self.borrowed_books = [
            {
                'id': 1,
                'borrower': 'Alice Johnson',
                'quantity': '15',
                'borrowed_date': (today - timedelta(days=10)).strftime('%Y-%m-%d'),
                'due_date': (today + timedelta(days=4)).strftime('%Y-%m-%d'),
                'status': 'Active'
            },
            {
                'id': 2,
                'borrower': 'Bob Smith',
                'quantity': '8',
                'borrowed_date': (today - timedelta(days=8)).strftime('%Y-%m-%d'),
                'due_date': (today + timedelta(days=6)).strftime('%Y-%m-%d'),
                'status': 'Active'
            },
            {
                'id': 3,
                'borrower': 'Carol Davis',
                'quantity': '23',
                'borrowed_date': (today - timedelta(days=12)).strftime('%Y-%m-%d'),
                'due_date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                'status': 'Active'
            },
            {
                'id': 4,
                'borrower': 'David Wilson',
                'quantity': '12',
                'borrowed_date': (today - timedelta(days=13)).strftime('%Y-%m-%d'),
                'due_date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                'status': 'Active'
            },
            {
                'id': 5,
                'borrower': 'Eva Martinez',
                'quantity': '7',
                'borrowed_date': (today - timedelta(days=11)).strftime('%Y-%m-%d'),
                'due_date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                'status': 'Active'
            }
        ]
        
    def init_ui(self):
        self.setWindowTitle("BJRS Library Management System")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1300, 700)
        self.showMaximized()
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Use QHBoxLayout for sidebar + content layout
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add sidebar
        self.sidebar = NavigationSidebar()

        # Set up navigation handler 
        self.sidebar.on_navigation_clicked = self.handle_navigation
        main_layout.addWidget(self.sidebar)
        
        # Content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        # Header
        header = self.create_header()
        content_layout.addWidget(header)
        
        # Stats section
        stats = self.create_stats_section()
        content_layout.addWidget(stats)
        
        # Due this week section
        due_books = self.create_due_books_section()
        content_layout.addWidget(due_books)
        
        main_layout.addWidget(content_widget)
        
        self.apply_styles()
    
    def handle_navigation(self, page_name):
        """Handle navigation clicks from sidebar"""
        print(f"Navigating to: {page_name}")
        print(f"Current librarian_id: {self.librarian_id}")  # Debug: show librarian_id when navigating
        
        # You can add actual navigation logic here
        # For example:
        if page_name == "Books":
            # Navigate to books page with librarian_id
            try:
                from booksPages import books1
                if books1:
                    self.books_window = books1.CollapsibleSidebar(librarian_id=self.librarian_id)  
                    self.books_window.show()
                    self.close()
                else:
                    print("Books module not available")
            except ImportError:
                print("Books module not found")
        elif page_name == "Members":
            # Navigate to members page
            print("Navigate to Members page")
        elif page_name == "Transactions":
            # Navigate to transactions page
            print("Navigate to Transactions page")
        elif page_name == "Settings":
            # Navigate to settings page
            print("Navigate to Settings page")
        # Dashboard is already showing, so no action needed for "Dashboard"
        
    def create_header(self):
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(120)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # Welcome text <BJRS Library Management System>
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(2)
        
        # Show librarian info if available
        if self.librarian_id:
            title_text = f"BJRS Library Management System - Librarian {self.librarian_id}"
        else:
            title_text = "BJRS Library Management System"
            
        self.welcome_label = QLabel(title_text)
        self.welcome_label.setObjectName("welcomeTitle")
        
        self.datetime_label = QLabel()
        self.datetime_label.setObjectName("dateTime")
        
        welcome_layout.addWidget(self.welcome_label)
        welcome_layout.addWidget(self.datetime_label)
        
        layout.addWidget(welcome_widget)
        layout.addStretch()
        
        return header
    
    def create_stats_section(self): # Container ni Stats 
        stats_widget = QFrame()
        stats_widget.setObjectName("statsContainer")
        layout = QGridLayout(stats_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Calculate dynamic stats
        total_books = 1847
        active_members = 342
        books_issued = len([book for book in self.borrowed_books if book['status'] == 'Active'])
        due_this_week = len(self.get_books_due_this_week())
        
        stats_data = [
            ("📚", f"{total_books:,}", "Total Books", "#3b82f6"),
            ("👥", f"{active_members}", "Active Members", "#10b981"),
            ("📋", f"{books_issued}", "Books Issued", "#f59e0b"),
            ("⏰", f"{due_this_week}", "Due This Week", "#ef4444")
        ]
        
        for i, (icon, number, label, color) in enumerate(stats_data):
            card = self.create_stat_card(icon, number, label, color)
            layout.addWidget(card, 0, i)
        
        return stats_widget
    
    def create_stat_card(self, icon, number, label, color): # container ni Stats 
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header with icon and number
        header_layout = QHBoxLayout()
        
        # Number and label
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
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setObjectName("statIcon")
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {color}; 
            border-radius:12px; 
            font-size: 24px;
            color: white;
            font-family: 'Times New Roman';
        """)
        
        header_layout.addWidget(text_widget)
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        
        layout.addLayout(header_layout)
        layout.addStretch()
        
        return card
    
    def create_due_books_section(self):
        section = QFrame()
        section.setObjectName("sectionCard")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel(" Books Due This Week")
        title_label.setObjectName("sectionTitle")

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Table for due books
        self.due_books_table = QTableWidget()
        self.setup_due_books_table()
        self.populate_due_books_table()
        
        layout.addWidget(self.due_books_table)
        
        return section
    
    def setup_due_books_table(self):
        headers = ["Borrower Name", "Quantity", "Borrowed Date", "Due Date", "Days Left"]
        
        self.due_books_table.setColumnCount(len(headers))
        self.due_books_table.setHorizontalHeaderLabels(headers)
        
        # Table settings
        self.due_books_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.due_books_table.setAlternatingRowColors(True)
        self.due_books_table.setGridStyle(Qt.SolidLine)
        self.due_books_table.setSortingEnabled(True)
        self.due_books_table.setMinimumHeight(300)
        
        # Column widths - improved for better text visibility
        header = self.due_books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Borrower Name
        header.setSectionResizeMode(1, QHeaderView.Fixed)    # Quantity
        header.setSectionResizeMode(2, QHeaderView.Fixed)    # Borrowed Date
        header.setSectionResizeMode(3, QHeaderView.Fixed)    # Due Date
        header.setSectionResizeMode(4, QHeaderView.Fixed)    # Days Left
        
        # Set wider column widths for better text visibility
        self.due_books_table.setColumnWidth(1, 120)  # Quantity
        self.due_books_table.setColumnWidth(2, 150)  # Borrowed Date
        self.due_books_table.setColumnWidth(3, 150)  # Due Date
        self.due_books_table.setColumnWidth(4, 120)  # Days Left
        
        # Set row height for better readability
        self.due_books_table.verticalHeader().setDefaultSectionSize(45)
        self.due_books_table.verticalHeader().hide()
    
    def get_books_due_this_week(self):
        """Get books that are due within the next 7 days"""
        today = datetime.now().date()
        week_end = today + timedelta(days=7)
        
        due_books = []
        for book in self.borrowed_books:
            if book['status'] == 'Active':
                due_date = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
                if today <= due_date <= week_end:
                    due_books.append(book)
        
        return due_books
    
    def populate_due_books_table(self):
        """Populate the table with books due this week"""
        due_books = self.get_books_due_this_week()
        self.due_books_table.setRowCount(len(due_books))
        
        for row, book in enumerate(due_books):
            # Calculate days left
            today = datetime.now().date()
            due_date = datetime.strptime(book['due_date'], '%Y-%m-%d').date()
            days_left = (due_date - today).days
            
            # Borrower Name
            borrower_item = QTableWidgetItem(book['borrower'])
            borrower_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.due_books_table.setItem(row, 0, borrower_item)
            
            # Quantity
            quantity_item = QTableWidgetItem(book['quantity'])
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.due_books_table.setItem(row, 1, quantity_item)
            
            # Borrowed Date
            borrowed_item = QTableWidgetItem(book['borrowed_date'])
            borrowed_item.setTextAlignment(Qt.AlignCenter)
            self.due_books_table.setItem(row, 2, borrowed_item)
            
            # Due date with color coding
            due_item = QTableWidgetItem(book['due_date'])
            due_item.setTextAlignment(Qt.AlignCenter)
            if days_left <= 1:
                due_item.setBackground(QColor("#fee2e2"))  # Light red for urgent
                due_item.setForeground(QColor("#dc2626"))  # Dark red text
            elif days_left <= 3:
                due_item.setBackground(QColor("#fef3c7"))  # Light yellow for warning
                due_item.setForeground(QColor("#d97706"))  # Dark yellow text
            self.due_books_table.setItem(row, 3, due_item)
            
            # Days left with color coding
            days_item = QTableWidgetItem(str(days_left))
            days_item.setTextAlignment(Qt.AlignCenter)
            if days_left <= 1:
                days_item.setBackground(QColor("#fee2e2"))
                days_item.setForeground(QColor("#dc2626"))
            elif days_left <= 3:
                days_item.setBackground(QColor("#fef3c7"))
                days_item.setForeground(QColor("#d97706"))
            self.due_books_table.setItem(row, 4, days_item)
    
    def filter_due_books(self, text):
        """Filter the due books table based on search text"""
        for row in range(self.due_books_table.rowCount()):
            match = False
            for col in range(self.due_books_table.columnCount()):
                item = self.due_books_table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.due_books_table.setRowHidden(row, not match)
    
    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(60000)  # Update every minute
        self.update_datetime()
    
    def update_datetime(self):
        now = datetime.now()
        formatted_time = now.strftime("%A, %B %d, %Y at %I:%M %p")
        self.datetime_label.setText(formatted_time)
    
    def apply_styles(self):
        """Apply consistent styling throughout the application"""
        style = """
        QMainWindow {
            background-color: #f1efe3;
            color: #5e3e1f;
            font-family: 'Times New Roman';
        }
        
        QFrame#headerFrame {
            background-color: #ffffff;
            border-radius: 12px;
            border: 2px solid #e8d8bd;
        }
        
        QFrame#statsContainer {
            background-color: #ffffff;
            border-radius: 12px;
            border: 2px solid #e8d8bd;
        }
        
        QLabel#welcomeTitle {
            color: #5e3e1f;
            font-size: 42px;
            font-weight: bold;
            font-family: 'Times New Roman';
        }
        
        QLabel#dateTime {
            color: #64748b;
            font-size: 14px;
            font-family: 'Times New Roman';
        }
        
        QFrame#statCard {
            background-color: #ffffff;
            border-radius: 12px;
            border: 2px solid #e8d8bd;
        }
        
        QLabel#statNumber {
            color: #5e3e1f;
            font-size: 30px;
            font-weight: bold;
            font-family: 'Times New Roman';
        }
        
        QLabel#statLabel {
            color: #64748b;
            font-size: 16px;
            letter-spacing: 0.5px;
            font-family: 'Times New Roman';
        }
        
        QFrame#sectionCard {
            background-color: #ffffff;
            border-radius: 12px;
            border: 2px solid #e8d8bd;
        }
        
        QLabel#sectionTitle {
            color: #5e3e1f;
            font-size: 20px;
            font-weight: 600;
            font-family: 'Times New Roman';
        }
        
        QTableWidget {
            background-color: #ffffff;
            border: 2px solid #e8d8bd;
            border-radius: 8px;
            gridline-color: #f1f5f9;
            font-size: 14px;
            color: #5e3e1f;
            font-family: 'Times New Roman';
        }
        
        QTableWidget::item {
            padding: 15px 12px;
            border-bottom: 1px solid #f1f5f9;
            color: #5e3e1f;
            font-family: 'Times New Roman';
        }
        
        QTableWidget::item:selected {
            background-color: #dbeafe;
            color: #1e40af;
        }
        
        QHeaderView::section {
            background-color: #f8fafc;
            color: #5e3e1f;
            font-size: 16px;
            padding: 15px 12px;
            border: none;
            font-family: 'Times New Roman';
            border-bottom: 2px solid #e5e7eb;
        }
        
        QTableWidget::item:alternate {
            background-color: #f8fafc;
        }
        
        QLabel {
            font-family: 'Times New Roman';
            font-size: 10px;
        }
        
        QWidget {
            font-family: 'Times New Roman';
        }
        """
        
        self.setStyleSheet(style)

def main(librarian_id=None):  # ← Added librarian_id parameter to main function
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    # Set global font to Times New Roman
    font = QFont("Times New Roman", 10)
    app.setFont(font)
  
    nav_manager.initialize(app)
    window = LibraryDashboard(librarian_id=librarian_id)  # ← Pass librarian_id to constructor
    nav_manager._current_window = window
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()