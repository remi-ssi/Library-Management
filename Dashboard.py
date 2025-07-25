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
from tryDatabase import DatabaseSeeder
from transactionPages.transaction_logic import BorrowBooks
from navbar_logic import nav_manager
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class LibraryDashboard(QMainWindow):
    def __init__(self, librarian_id=None):  
        # Initializes the main dashboard window, sets up the database, UI, and timers
        super().__init__()
        db_path = "bjrsLib.db"
        self.db_path = db_path
        self.db_seeder = DatabaseSeeder()
        self.librarian_id = librarian_id  
        self.borrowed_books = []
        
        self.init_ui()
        self.setup_timer()
        
        QTimer.singleShot(100, self.refresh_all_data)

    def init_ui(self):
        # Sets up the main layout, sidebar, header, stats, and due books section
        self.setWindowTitle("BJRS Library Management System")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1300, 700)
        self.showMaximized()
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = NavigationSidebar()
        self.sidebar.on_navigation_clicked = lambda item_name: nav_manager.handle_navigation(item_name, self.librarian_id)
        main_layout.addWidget(self.sidebar)
        
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(20)
        
        header = self.create_header()
        self.content_layout.addWidget(header)
        
        stats = self.create_stats_section()
        self.content_layout.addWidget(stats)
        
        due_books = self.create_due_books_section()
        self.content_layout.addWidget(due_books)
        
        main_layout.addWidget(content_widget)
        
        self.apply_styles()

    def refresh_all_data(self):
        # Refreshes all dashboard data: stats, due books, and current date/time
        try:
            self.borrowed_books = self.get_borrow_transactions()
            
            for i in reversed(range(self.content_layout.count())):
                widget = self.content_layout.itemAt(i).widget()
                if widget and widget.objectName() == "statsContainer":
                    widget.setParent(None)
                    break
                    
            stats_widget = self.create_stats_section()
            self.content_layout.insertWidget(1, stats_widget)
                
            self.populate_due_books_table()
            
            self.update_datetime()
            
        except Exception as e:
            print(f"Error refreshing data: {e}")

    def showEvent(self, event):
        # Ensures data is refreshed every time the dashboard window is shown
        super().showEvent(event)
        self.refresh_all_data()

    def create_header(self):
        # Builds the header section with the app title and current date/time
        header = QFrame()
        header.setObjectName("headerFrame")
        header.setFixedHeight(120)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(30, 20, 30, 20)
        
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setContentsMargins(0, 0, 0, 0)
        welcome_layout.setSpacing(2)
        
        if self.librarian_id:
            title_text = f"BJRS Library Management System"
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

    def get_borrow_transactions(self):
        # Fetches all borrow transactions for the current librarian and calculates days left for each
        try:
            borrow_manager = BorrowBooks()
            transactions = borrow_manager.fetch_transaction(self.librarian_id) or []
            
            today = datetime.now().date()
            transactions_dict = {}
            
            for trans in transactions:
                if trans.get('action') != 'Borrowed':
                    continue
                    
                trans_id = trans.get('id')
                due_date_str = trans.get('due_date', '')
                
                try:
                    # Calculate days left properly
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date() if due_date_str else None
                    days_left = (due_date - today).days if due_date else 0
                except (ValueError, TypeError) as e:
                    print(f"Error parsing due date for transaction {trans_id}: {e}")
                    days_left = 0
                    
                if trans_id not in transactions_dict:
                    transactions_dict[trans_id] = {
                        'id': trans_id,
                        'borrower': trans.get('borrower', 'N/A'),
                        'borrowed_date': trans.get('date', 'N/A'),
                        'due_date': due_date_str,
                        'days_left': days_left,  # Store calculated days left
                        'status': 'Borrowed',  # Default status
                        'books': [],
                        'quantity': 0
                    }
                    
                transactions_dict[trans_id]['books'].append({
                    'title': trans.get('book_title', 'N/A'),
                    'quantity': trans.get('quantity', 1)
                })
                transactions_dict[trans_id]['quantity'] += trans.get('quantity', 1)
                
            return list(transactions_dict.values())
        except Exception as e:
            QMessageBox.warning(self, "Fetch Error", f"Failed to fetch transactions: {str(e)}")
            return []

    def create_stats_section(self):
        # Creates the statistics section showing total books, members, issued books, and books due soon
        stats_widget = QFrame()
        stats_widget.setObjectName("statsContainer")
        layout = QGridLayout(stats_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        if not isinstance(self.borrowed_books, list):
            self.borrowed_books = self.get_borrow_transactions()

        total_books = self.db_seeder.dashboardCount(tableName="Book", id=self.librarian_id) or 0
        active_members = self.db_seeder.dashboardCount(tableName="Member", id=self.librarian_id) or 0
        books_issued = self.db_seeder.dashboardCount(tableName="BookTransaction", id=self.librarian_id) or 0 
        due_this_week = len(self.get_books_due_this_week())
        
        stats_data = [
            ("📚", f"{total_books}", "Total Books", "#3b82f6"),
            ("👥", f"{active_members}", "Active Members", "#10b981"),
            ("📋", f"{books_issued}", "Books Issued", "#f59e0b"),
            ("⏰", f"{due_this_week}", "Due In A Week", "#ef4444")
        ]
        
        for i, (icon, number, label, color) in enumerate(stats_data):
            card = self.create_stat_card(icon, number, label, color)
            layout.addWidget(card, 0, i)
        
        return stats_widget

    def create_stat_card(self, icon, number, label, color):
        # Helper to build a single stat card for the stats section
        card = QFrame()
        card.setObjectName("statCard")
        card.setFixedHeight(100)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        # Builds the section that lists books due within a week
        section = QFrame()
        section.setObjectName("sectionCard")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        header_layout = QHBoxLayout()
        title_label = QLabel("Books In A Week")
        title_label.setObjectName("sectionTitle")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        self.due_books_table = QTableWidget()
        self.setup_due_books_table()
        layout.addWidget(self.due_books_table)
        
        return section

    def setup_due_books_table(self):
        # Configures the columns and appearance of the due books table
        headers = ["Borrower Name", "Quantity", "Borrowed Date", "Due Date", "Days Left"]
        
        self.due_books_table.setColumnCount(len(headers))
        self.due_books_table.setHorizontalHeaderLabels(headers)
        self.due_books_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.due_books_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.due_books_table.setAlternatingRowColors(False)
        self.due_books_table.setGridStyle(Qt.SolidLine)
        self.due_books_table.setSortingEnabled(False)
        self.due_books_table.setMinimumHeight(300)
        
        header = self.due_books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        
        self.due_books_table.setColumnWidth(1, 120)
        self.due_books_table.setColumnWidth(2, 150)
        self.due_books_table.setColumnWidth(3, 150)
        self.due_books_table.setColumnWidth(4, 120)
        
        self.due_books_table.verticalHeader().setDefaultSectionSize(45)
        self.due_books_table.verticalHeader().hide()

    def get_books_due_this_week(self):
        # Returns a list of borrowed books that are due within the next 7 days or are overdue
        if not self.borrowed_books:
            self.borrowed_books = self.get_borrow_transactions()
        
        active_books = []
        
        for book in self.borrowed_books:
            try:
                days_left = book.get('days_left', 0)
                # Only include books due within 7 days or overdue
                if days_left <= 7:
                    active_books.append({
                        **book,
                        'status': 'Overdue' if days_left < 0 else 'Borrowed'  # Only < 0 is overdue
                    })
            except (ValueError, KeyError) as e:
                print(f"Error processing book {book.get('id')}: {e}")
                continue
        
        return active_books

    def populate_due_books_table(self):
        # Fills the due books table with data about books due soon or overdue
        active_books = self.get_books_due_this_week()
        
        self.due_books_table.setRowCount(0)
        self.due_books_table.setRowCount(len(active_books))

        for row, book in enumerate(active_books):
            borrower_item = QTableWidgetItem(book['borrower'])
            borrower_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.due_books_table.setItem(row, 0, borrower_item)
            
            quantity_item = QTableWidgetItem(str(book.get('quantity', 1)))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.due_books_table.setItem(row, 1, quantity_item)
            
            borrowed_item = QTableWidgetItem(book['borrowed_date'])
            borrowed_item.setTextAlignment(Qt.AlignCenter)
            self.due_books_table.setItem(row, 2, borrowed_item)
            
            due_item = QTableWidgetItem(book['due_date'])
            due_item.setTextAlignment(Qt.AlignCenter)
            
            days_left = book.get('days_left', 0)
            if days_left < 0:  # Only < 0 is overdue
                due_item.setBackground(QColor("#fee2e2"))
                due_item.setForeground(QColor("#dc2626"))
            elif days_left <= 3:
                due_item.setBackground(QColor("#fef3c7"))
                due_item.setForeground(QColor("#d97706"))
            self.due_books_table.setItem(row, 3, due_item)
            
            # Show "Overdue" only when days_left < 0
            days_text = "Overdue" if days_left < 0 else str(days_left)
            
            days_item = QTableWidgetItem(days_text)
            days_item.setTextAlignment(Qt.AlignCenter)
            if days_left < 0:
                days_item.setBackground(QColor("#fee2e2"))
                days_item.setForeground(QColor("#dc2626"))
            elif days_left <= 3:
                days_item.setBackground(QColor("#fef3c7"))
                days_item.setForeground(QColor("#d97706"))
            self.due_books_table.setItem(row, 4, days_item)

    def setup_timer(self):
        # Starts a timer to update the date/time label every minute
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_datetime)
        self.timer.start(60000)
        self.update_datetime()

    def update_datetime(self):
        # Updates the date/time label in the header with the current time
        now = datetime.now()
        formatted_time = now.strftime("%A, %B %d, %Y at %I:%M %p")
        self.datetime_label.setText(formatted_time)

    def apply_styles(self):
        # Applies the custom stylesheet for the dashboard UI
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
            background-color: #e8d8bd;
            color: #5e3e1f;
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

def main(librarian_id=None):
    # Entry point for the application. Sets up the app, font, and shows the dashboard window
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    font = QFont("Times New Roman", 10)
    app.setFont(font)
  
    nav_manager.initialize(app)
    window = LibraryDashboard(librarian_id=librarian_id)
    nav_manager._current_window = window
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()