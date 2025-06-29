import sys
import requests
import navigation_sidebar
from navbar_logic import nav_manager
from .transaction_logic import BorrowBooks

from datetime import datetime, timedelta
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QTimer, QRect, QEasingCurve
from PySide6.QtGui import QFont, QIcon, QPixmap, QPainter, QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QLineEdit, QScrollArea, QGridLayout,
    QTabWidget, QTextEdit, QMessageBox, QFormLayout, QDialog, QListWidget,
    QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QStackedWidget, QMainWindow, QComboBox, QDateEdit
)
from PySide6.QtCore import QDate
from functools import partial
from .AddTransactionForm import AddTransactionForm
from navigation_sidebar import NavigationSidebar  
from navbar_logic import nav_manager  

class TransactionCard(QFrame):
    def __init__(self, transaction, parent_system):
        super().__init__()
        self.transaction = transaction
        self.parent_system = parent_system
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget() 
        self.setFrameStyle(QFrame.Box)
        self.setCentralWidget(central_widget)
        self.setStyleSheet("""
            QFrame {
                background-color: #e8d8bd;
                border-radius: 15px;
            }
            QFrame:hover {
                border-color: #5e3e1f;
                background-color: #5e3e1f;
            }
        """)
        self.showMaximized()

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # Transaction ID (always at the top, left-aligned)
        id_label = QLabel(f"Transaction ID: {self.transaction['id']}")
        id_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        id_label.setStyleSheet("color: #8B4513; background: none; border: none; margin-bottom: 2px;")
        id_label.setFrameStyle(QFrame.NoFrame)
        id_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        id_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(id_label)

        # Book title
        title_label = QLabel(f"Book: {self.transaction['book_title']}")
        title_label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        title_label.setWordWrap(True)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #8B4513; background: none; border: none; margin-bottom: 4px;")
        title_label.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(title_label)

        # Borrower name
        borrower_label = QLabel(f"Borrower: {self.transaction['borrower']}")
        borrower_label.setFont(QFont("Times New Roman", 10))
        borrower_label.setAlignment(Qt.AlignCenter)
        borrower_label.setStyleSheet("color: #e8d8bd; background: none; border: none; margin-bottom: 8px;")
        borrower_label.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(borrower_label)

        # Date
        date_label = QLabel(f"Date: {self.transaction['date']}")
        date_label.setFont(QFont("Times New Roman", 10))
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #8B7B6A; background: none; border: none;")
        date_label.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(date_label)

        # Due date (if applicable)
        if self.transaction.get('due_date'):
            due_label = QLabel(f"Due: {self.transaction['due_date']}")
            due_label.setFont(QFont("Times New Roman", 10))
            due_label.setAlignment(Qt.AlignCenter)
            if self.transaction['action'] == 'Borrowed':
                due_date = datetime.strptime(self.transaction['due_date'], "%Y-%m-%d")
                today = datetime.now()
                if due_date < today:
                    due_label.setStyleSheet("color: #e74c3c; font-weight: bold; background: none; border: none;")
                else:
                    due_label.setStyleSheet("color: #27ae60; background: none; border: none;")
            else:
                due_label.setStyleSheet("color: #888; background: none; border: none;")
            due_label.setFrameStyle(QFrame.NoFrame)
            layout.addWidget(due_label)

        layout.addStretch()

        # Status indicator at bottom
        if self.transaction['action'] == 'Borrowed':
            due_date = datetime.strptime(self.transaction['due_date'], "%Y-%m-%d")
            today = datetime.now()
            if due_date < today:
                status_label = QLabel("OVERDUE")
                status_label.setStyleSheet("""
                    background-color: #5e3e1f;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 10px;
                """)
            else:
                status_label = QLabel("ACTIVE")
                status_label.setStyleSheet("""
                    background-color: #8B4513;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 10px;
                """)
        else:
            status_label = QLabel("RETURNED")
            status_label.setStyleSheet("""
                background-color: #8B4513;
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 10px;
            """)

        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)

class LibraryTransactionSystem(QMainWindow):
    def __init__(self, librarian_id=None):
        super().__init__()
        self.librarian_id = librarian_id
        self.borrow_books = BorrowBooks() # Initialize BorrowBooks instance
        self.setGeometry(100, 100, 1400, 800)
        self.setStyleSheet("background-color: white;")
        self.showMaximized()
        self.transactions = []
        self.next_transaction_id = 1
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # MAIN HORIZONTAL LAYOUT for sidebar + content
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add sidebar to the left
        self.sidebar = NavigationSidebar()
        self.sidebar.on_navigation_clicked = nav_manager.handle_navigation
        main_layout.addWidget(self.sidebar)

        # Create content area widget
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f3ed;")
        main_layout.addWidget(content_widget)

        # Content layout (vertical)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # Header
        header_widget = QWidget()
        header_widget.setFixedHeight(100)
        header_widget.setStyleSheet("background-color: #f5f3ed;")
        content_layout.addWidget(header_widget)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 20, 40, 20)
        header_layout.setSpacing(20)
        title_label = QLabel("Transaction Management")
        title_label.setFont(QFont("Times New Roman", 32, QFont.Bold))
        title_label.setStyleSheet("color: #5e3e1f; margin-right: 20px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Navigation
        nav_widget = QWidget()
        nav_widget.setFixedHeight(60)
        nav_widget.setStyleSheet("background-color: white; border-bottom: 1px solid #e8d8bd;")
        content_layout.addWidget(nav_widget)
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(80, 10, 80, 10)
        nav_layout.setSpacing(10)
        self.transactions_btn = QPushButton("Current Transactions")
        self.transactions_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.transactions_btn.setFixedSize(180, 40)
        self.transactions_btn.clicked.connect(self.show_transactions_page)
        nav_layout.addWidget(self.transactions_btn)
        self.history_btn = QPushButton("Transaction History")
        self.history_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.history_btn.setFixedSize(180, 40)
        self.history_btn.clicked.connect(self.show_history_page)
        nav_layout.addWidget(self.history_btn)

        # Content area
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        self.create_transactions_page()
        self.create_history_page()
        self.show_transactions_page()

    # ... rest of your methods remain the same ...
    def create_transactions_page(self):
        self.transactions_page = QWidget()
        self.transactions_page.setStyleSheet("background-color: #f5f3ed;")
        layout = QVBoxLayout(self.transactions_page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.trans_search_edit = QLineEdit()
        self.trans_search_edit.setPlaceholderText("Search transactions...")
        self.trans_search_edit.setFont(QFont("Times New Roman", 14))
        self.trans_search_edit.setFixedHeight(45)
        self.trans_search_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e8d8bd;
                border-radius: 10px;
                background-color: #fff;
                color: #5e3e1f;
                font-family: 'Times New Roman';
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: #f5f3ed;
            }
        """)
        self.trans_search_edit.textChanged.connect(self.search_transactions)
        search_layout.addWidget(self.trans_search_edit)
        add_transaction_btn = QPushButton("➕")
        add_transaction_btn.setStyleSheet("""
            QPushButton {
                color: #5e3e1f;
                font-size: 22px;
                font-weight: bold;
                background-color: #fff;
                border: 2px solid #e8d8bd;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5e3e1f;
                color: #fff;
            }
        """)
        add_transaction_btn.clicked.connect(self.open_add_transaction_form)
        search_layout.addWidget(add_transaction_btn)
        layout.addLayout(search_layout)
        self.trans_table = QTableWidget()
        self.trans_table.setColumnCount(6)
        self.trans_table.setHorizontalHeaderLabels([
            "Name", "Book Borrowed", "Borrowed Date", "Transaction Type", "Returned Date", ""
        ])
        self.trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trans_table.verticalHeader().setVisible(False)
        self.trans_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trans_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.trans_table.setAlternatingRowColors(False)
        self.trans_table.setShowGrid(True)
        layout.addWidget(self.trans_table, stretch=1)
        self.setup_table_style(self.trans_table)
        self.content_stack.addWidget(self.transactions_page)

    def create_history_page(self):
        self.history_page = QWidget()
        self.history_page.setStyleSheet("background-color:#f5f3ed;")
        layout = QVBoxLayout(self.history_page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        self.hist_search_edit = QLineEdit()
        self.hist_search_edit.setPlaceholderText("Search history...")
        self.hist_search_edit.setFont(QFont("Times New Roman", 14))
        self.hist_search_edit.setFixedHeight(45)
        self.hist_search_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                background-color: #fafafa;
                color: #5C4033;
            }
            QLineEdit:focus {
                border-color: #e8d8bd;
                background-color: white;
            }
        """)
        self.hist_search_edit.textChanged.connect(self.search_history)
        search_layout.addWidget(self.hist_search_edit)
        layout.addLayout(search_layout)
        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(6)
        self.hist_table.setHorizontalHeaderLabels([
            "Borrower", "Book Title", "Borrowed Date", "Returned Date", "Status", " "
        ])
        self.hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hist_table.verticalHeader().setVisible(False)
        self.hist_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hist_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.hist_table.setAlternatingRowColors(False)
        self.hist_table.setShowGrid(True)
        layout.addWidget(self.hist_table, stretch=1)
        self.setup_table_style(self.hist_table)
        self.content_stack.addWidget(self.history_page)

    def show_transactions_page(self):
        self.content_stack.setCurrentWidget(self.transactions_page)
        # Active button style
        self.transactions_btn.setStyleSheet("""
            QPushButton {
                background-color: #5e3e1f;
                color: white;
                font-weight: bold;
                border-radius: 20px;
                border: 2px solid #5e3e1f;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5e3e1f;
                border-color: #5e3e1f;
            }
        """)
        # Inactive button style
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8B4513;
                font-weight: normal;
                border-radius: 20px;
                border: 2px solid #e8d8bd;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: ##5e3e1f;
                border-color: #8B4513; 
            }
        """)
        self.display_transactions()

    def show_history_page(self):
        self.content_stack.setCurrentWidget(self.history_page)
        # Active button style
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B4513;
                color: white;
                font-weight: bold;
                border-radius: 20px;
                border: 2px solid #8B4513;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5e3e1f;
                border-color: #5e3e1f;
            }
        """)
        # Inactive button style
        self.transactions_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8B4513;
                font-weight: normal;
                border-radius: 20px;
                border: 2px solid #e8d8bd;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #f5f3ed;
                border-color: #8B4513;
            }
        """)
        self.display_history()

    def display_transactions(self, filtered_transactions=None):
        from PySide6.QtGui import QColor
        active_transactions = [t for t in self.transactions if t['action'] == 'Borrowed']
        transactions_to_display = filtered_transactions if filtered_transactions is not None else active_transactions

        self.trans_table.setRowCount(len(transactions_to_display))
        for row, trans in enumerate(transactions_to_display):
            # Status logic
            status = ""
            if trans['action'] == 'Borrowed':
                due_date = datetime.strptime(trans['due_date'], "%Y-%m-%d")
                today = datetime.now()
                if due_date < today:
                    status = "Overdue"
                else:
                    status = "Active"

            values = [
                trans['borrower'],
                trans['book_title'],
                trans['date'],
                "Borrowed",  #always shows borrowed 
                trans.get('returned_date', ''),  # Returned Date (will be empty for borrowed) 
            ]

            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setForeground(QColor("#5C4033"))
                if col == 3:  # Status column
                    if status == "OVERDUE":
                        item.setForeground(QColor("#c0392b"))
                    elif status == "ACTIVE":
                        item.setForeground(QColor("#27ae60"))
                self.trans_table.setItem(row, col, item)


            # --- Delete button ---
            delete_btn = QPushButton("Delete")
            delete_btn.setToolTip("Delete Transaction")
            delete_btn.setFont(QFont("Segoe UI Emoji", 10, QFont.Bold))
            delete_btn.setStyleSheet("""
                QPushButton {
                    border-radius: 12px;
                    font-size: 10px;
                    color: #c0392b;
                    background: white;
                    font-family: "Segoe UI Emoji", "Times New Roman";
                    font-weight: bold;
                    border: 2px solid #c0392b;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_btn.clicked.connect(partial(self.delete_transaction, row, transactions_to_display))

            # Center the button in the cell
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.addStretch()
            layout.addWidget(delete_btn)
            layout.addStretch()
            layout.setContentsMargins(0, 0, 0, 0)
            self.trans_table.setCellWidget(row, 5, container)

            self.trans_table.setRowHeight(row, 40)  

    def search_transactions(self):
        search_term = self.trans_search_edit.text().lower()
        active_transactions = [t for t in self.transactions if t['action'] == 'Borrowed']
        if not search_term:
            self.display_transactions()
        else:
            filtered_transactions = [
                trans for trans in active_transactions
                if search_term in trans['book_title'].lower() or search_term in trans['borrower'].lower()
            ]
            self.display_transactions(filtered_transactions)

    def display_history(self, filtered_history=None):
        from PySide6.QtGui import QColor
        sorted_transactions = sorted(self.transactions, key=lambda x: x['date'], reverse=True)
        history_to_display = filtered_history if filtered_history is not None else sorted_transactions

        self.hist_table.setRowCount(len(history_to_display))
        for row, trans in enumerate(history_to_display):
            values = [
                trans['borrower'],
                trans['book_title'],
                trans['date'],
                trans.get('returned_date', 'N/A'),
                "Active" if trans['action'] == "Borrowed" else "Returned"
            ]
            # Set text columns
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setForeground(QColor("#5C4033"))
                if col == 4:
                    if value == "Active":
                        item.setForeground(QColor("#27ae60"))
                    else:
                        item.setForeground(QColor("#8B4513"))
                self.hist_table.setItem(row, col, item)

            # Add Delete button in last column of Transaction History
            delete_btn = QPushButton("Delete")
            delete_btn.setToolTip("Delete Transaction Historty")
            delete_btn.setFont(QFont("Times New Roman", 10, QFont.Bold))
            delete_btn.setStyleSheet("""
                QPushButton {
                    border-radius: 12px;
                    font-size: 10px;
                    color: #c0392b;
                    background: white;
                    font-family: "Segoe UI Emoji", "Times New Roman";
                    font-weight: bold;
                    border: 2px solid #c0392b;
                    padding:5px 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                    color: white;
                }
            """)
            delete_btn.clicked.connect(partial(self.delete_transaction, trans))

            # Center the button using a layout
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addStretch()
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            actions_layout.setContentsMargins(0, 0, 0, 0)

            self.hist_table.setCellWidget(row, 5, actions_widget)
            self.hist_table.setRowHeight(row, 40)

    def search_history(self):
        search_term = self.hist_search_edit.text().lower()
        if not search_term:
            self.display_history()
        else:
            filtered_history = [
                trans for trans in self.transactions
                if search_term in trans['book_title'].lower()
                or search_term in trans['borrower'].lower()
                or search_term in trans['action'].lower()
            ]
            self.display_history(filtered_history)

    def open_add_transaction_form(self):
        # Use unique book titles from transactions as a fallback
        books_list = list({t['book_title'] for t in self.transactions})
        dialog = AddTransactionForm(books_list, self)
        if dialog.exec():
            borrower = dialog.borrower_edit.text()
            book = dialog.book_combo.currentText()
            borrow_date = dialog.borrow_date_edit.date().toString("yyyy-MM-dd")
            due_date = dialog.due_date_edit.date().toString("yyyy-MM-dd")
            status = dialog.status_combo.currentText()
            new_transaction = {
                "id": self.next_transaction_id,
                "book_title": book,
                "borrower": borrower,
                "action": status,
                "date": borrow_date,
                "due_date": due_date
            }
            self.transactions.append(new_transaction)
            self.next_transaction_id += 1
            self.display_transactions()
            self.display_history()

    def open_edit_transaction_form(self, transaction):
        books_list = list({t['book_title'] for t in self.transactions})
        dialog = AddTransactionForm(books_list, self)
        # Pre-fill fields
        dialog.borrower_edit.setText(transaction['borrower'])
        dialog.book_combo.setCurrentText(transaction['book_title'])
        dialog.borrow_date_edit.setDate(QDate.fromString(transaction['date'], "yyyy-MM-dd"))
        dialog.due_date_edit.setDate(QDate.fromString(transaction['due_date'], "yyyy-MM-dd"))
        dialog.status_combo.setCurrentText(transaction['action'])

        if dialog.exec():
            transaction['borrower'] = dialog.borrower_edit.text()
            transaction['book_title'] = dialog.book_combo.currentText()
            transaction['date'] = dialog.borrow_date_edit.date().toString("yyyy-MM-dd")
            transaction['due_date'] = dialog.due_date_edit.date().toString("yyyy-MM-dd")
            transaction['action'] = dialog.status_combo.currentText()
            self.display_transactions()
            self.display_history()

    def delete_transaction(self, transaction):
        # Remove from the main transactions list
        self.transactions = [t for t in self.transactions if t['id'] != transaction['id']]
        # Refresh the table and history
        self.display_transactions()
        self.display_history()

    def setup_table_style(self, table):
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e8d8bd-;
                border-radius: 8px;
                gridline-color: #e8d8bd;
                font-family: 'Times New Roman';
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #f5f3ed;
                color: #5e3e1f;
            }
            QHeaderView::section {
                background-color: #5e3e1f;
                color: White;
                font-weight: bold;
                font-family: 'Times New Roman';
                font-size: 16px;
                padding: 10px;
                border: none;
                border-right: 1px solid #5e3e1f;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)

# To run the app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize navigation manager
    nav_manager.initialize(app)
    
    window = LibraryTransactionSystem()
    window.showMaximized()
    nav_manager._current_window = window  # Set as current window
    sys.exit(app.exec())