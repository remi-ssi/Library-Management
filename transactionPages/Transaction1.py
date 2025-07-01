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
from .AddTransactionForm import AddTransactionForm  # PARA MA-IMPORT UNG TRANSACTION FORM 
from .PreviewTransactionForm import PreviewTransactionForm # PARA MA-IMPORT UNG PREVIEW NG TRANSACTION
from .HistoryPreviewForm import HistoryTransactionPreviewForm # PARA MA-IMPORT UNG PREVIEW NG HISTORY 
from navigation_sidebar import NavigationSidebar # PARA SA SIDE BAR 

class TransactionCard(QFrame):
    def __init__(self, transaction, parent_system):
        super().__init__()
        self.transaction = transaction
        self.parent_system = parent_system
        self.setup_ui()
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setFixedSize(280, 210)  
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

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

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

        # Due date 
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

        if self.transaction['action'] == 'Returned' and self.transaction.get('returned_date'):
            returned_label = QLabel(f"Returned: {self.transaction['returned_date']}")
            returned_label.setFont(QFont("Times New Roman", 10))
            returned_label.setAlignment(Qt.AlignCenter)
            returned_label.setStyleSheet("color: #8B4513; background: none; border: none;")
            layout.addWidget(returned_label)

        layout.addStretch()

        if self.transaction['action'] == 'Returned' and self.transaction.get('returned_date'):
            returned_label = QLabel(f"Returned: {self.transaction['returned_date']}")
            returned_label.setFont(QFont("Times New Roman", 10))
            returned_label.setAlignment(Qt.AlignCenter)
            returned_label.setStyleSheet("color: #8B4513; background: none; border: none;")
            layout.addWidget(returned_label)

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
                status_label = QLabel("Overdue")
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
        self.showMaximized()
        self.setStyleSheet("background-color: white;")
        self.showMaximized()
        self.transactions = []
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)      

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)

        self.sidebar = NavigationSidebar()
        self.sidebar.navigation_clicked.connect(
            lambda item_name: nav_manager.handle_navigation(item_name, self.librarian_id)
        )
        
        main_layout.addWidget(self.sidebar)

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f3ed;")
        main_layout.addWidget(content_widget)

        content_layout= QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0,0,0,0)
        content_layout.setSpacing(0)

        # Header
        header_widget = QWidget()
        header_widget.setFixedHeight(100)
        header_widget.setStyleSheet("background-color: #f5f3ed;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 20, 40, 20)
        header_layout.setSpacing(20)
        title_label = QLabel("Books Management")
        title_label.setFont(QFont("Times New Roman", 32, QFont.Bold))
        title_label.setStyleSheet("color: #5e3e1f; margin-right: 20px;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        content_layout.addWidget(header_widget)

        # Navigation
        nav_widget = QWidget()
        nav_widget.setFixedHeight(60)
        nav_widget.setStyleSheet("background-color: white; border-bottom: 1px solid #e8d8bd;")
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
        content_layout.addWidget(nav_widget)

        # Content 
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        self.create_transactions_page()
        self.create_history_page()
        self.show_transactions_page()


        # TRANSACTION PAGE
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
        # ADD BUTTON (Add Transaction)
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
            "Name", "Book Borrowed", "Borrowed Date", "Transaction Type", "Due Date", ""
        ])
        self.trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.trans_table.verticalHeader().setVisible(False)
        self.trans_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.trans_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.trans_table.setAlternatingRowColors(False)
        self.trans_table.setShowGrid(True)
        
        layout.addWidget(self.trans_table, stretch=1)
        self.setup_table_style(self.trans_table)
        self.trans_table.cellDoubleClicked.connect(self.on_transaction_double_click)  # double-click signal to see preview
        self.content_stack.addWidget(self.transactions_page)


    # HISTORY PAGE 
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
            "Borrower", "Book Title", "Borrowed Date", "Returned Date", "Due Date", "Status", " "
        ])
        self.hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hist_table.verticalHeader().setVisible(False)
        self.hist_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.hist_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.hist_table.setAlternatingRowColors(False)
        self.hist_table.setShowGrid(True)
        layout.addWidget(self.hist_table, stretch=1)
        self.setup_table_style(self.hist_table)
        self.hist_table.cellDoubleClicked.connect(self.on_history_double_click)
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
        # Always fetch all transactions for the current librarian
        self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id) or []
        print("Transaction(Current):", self.transactions)
        # Only show transactions where action is "Borrowed"
        transaction_dict = {}
        for trans in self.transactions:
            if trans.get('action') != 'Borrowed':
                continue
            trans_id = trans.get('id')
            if trans_id not in transaction_dict:
                transaction_dict[trans_id]  = {
                    'id': trans_id,
                    'borrower': trans.get('borrower', 'N/A'),
                    'date': trans.get('date', 'N/A'),
                    'due_date':trans.get('due_date', 'N/A'),
                    'action': trans.get('action', 'Borrowed'),
                    'remarks': trans.get('remarks', ''),
                    'books': []
                }
            transaction_dict[trans_id]['books'].append({
                'title': trans.get('book_title', 'N/A'),
                'quantity':trans.get('quantity', 1)
            })
        all_transactions = list(transaction_dict.values())
        transactions_to_display = filtered_transactions if filtered_transactions is not None else all_transactions
        self.trans_table.setRowCount(len(transactions_to_display))
        for row, trans in enumerate(transactions_to_display):
            due_date = datetime.strptime(trans['due_date'], "%Y-%m-%d")
            today = datetime.now()
            status = "Overdue" if due_date < today else "Active"

            book_titles = ", ".join([f"{book['title']} (x{book['quantity']})" for book in trans['books']])
            total_quantity = sum(book['quantity'] for book in trans['books'])
            values = [
                trans.get('borrower', 'N/A'),
                book_titles,
                trans.get('date', 'N/A'),
                status,
                trans.get('due_date', 'N/A'),
                str(total_quantity),
                ""
            ]
            
            
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setForeground(QColor("#5C4033"))
                if col == 3:  # Status column
                    if status == "Overdue":
                        item.setForeground(QColor("#c0392b"))
                    elif status == "Active":
                        item.setForeground(QColor("#27ae60"))
                    elif status == "Returned":
                        item.setForeground(QColor("#8B4513"))
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
            delete_btn.clicked.connect(partial(self.delete_transaction, trans))

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
        active_transactions = [t for t in self.transactions if t.get('action') == 'Borrowed']
        if not search_term:
            self.display_transactions()
        else:
            transaction_dict = {}
            for trans in self.transactions:
                if trans.get('action') != 'Borrowed':
                    continue
                trans_id = trans.get('id')
                if trans_id not in transaction_dict:
                    transaction_dict[trans_id]  = {
                        'id': trans_id,
                        'borrower': trans.get('borrower', 'N/A'),
                        'date': trans.get('date', 'N/A'),
                        'due_date':trans.get('due_date', 'N/A'),
                        'action': trans.get('action', 'Borrowed'),
                        'remarks': trans.get('remarks', ''),
                        'books': []
                    }
                transaction_dict[trans_id]['books'].append({
                    'title': trans.get('book_title', 'N/A'),
                    'quantity':trans.get('quantity', 1)
                })
            filtered_transactions = [
                trans for trans in transaction_dict.values()
                if search_term in trans['borrower'].lower() or 
                any(search_term in book['title'].lower() for book in trans['books'] )
            ]
            self.display_transactions(filtered_transactions)

    def display_history(self, filtered_history=None):
        from PySide6.QtGui import QColor
        self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id) or []
        print("Transactions (History):", self.transactions)
        history_to_display = filtered_history if filtered_history is not None else [
            t for t in self.transactions if t.get('action') == 'Returned'
        ]

        self.hist_table.setRowCount(len(history_to_display))
        for row, trans in enumerate(history_to_display):
            values = [
                trans.get('borrower', 'N/A'),
                trans.get('book_title', 'N/A'),
                trans.get('date', 'N/A'),
                trans.get('returned_date', 'N/A'),
                trans.get('due_date', 'N/A'),
                trans.get('action', 'N/A'),
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

            # Delete button on the Transaction History
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

            # Center the button using layout
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
                if (trans.get('action') == 'Returned' and
                (search_term in trans.get('book_title', '').lower()
                or search_term in trans.get('borrower', '').lower()
                or search_term in trans.get('returned_date', '').lower()
                or search_term in trans.get('action', '').lower()))
            ]
            self.display_history(filtered_history)

    def open_add_transaction_form(self):
        books = self.borrow_books.fetch_books(self.librarian_id)
        if not books:
            QMessageBox.critical(self, "Error", "No books available. Please add books to the database.")

        dialog = AddTransactionForm(librarian_id=self.librarian_id, parent=self)
        if dialog.exec():
           
            books_data = dialog.get_books_data()
            success = self.borrow_books.add_transaction(
                borrower_name=dialog.borrower_edit.text(),
                books_data=books_data,
                borrow_date=dialog.borrow_date_edit.date(),
                due_date=dialog.due_date_edit.date(),
                status=dialog.status_combo.currentText(),
                librarian_id=self.librarian_id
            )
            if success:
                self.transactions = self.borrow_books.fetch_all_transaction(self.librarian_id)
                self.display_transactions()
                self.display_history()

    def open_edit_transaction(self, selected_transaction):
        transaction_id = selected_transaction.get('id')
        if not transaction_id:
            print("Error: Missing TransactionID")
            QMessageBox.warning(self, "Error", "Invalid transactionID")
            return
        
        # Aggregate all transaction details for this TransactionID
        related_transactions = [t for t in self.transactions if t['id'] == transaction_id]
        books = [
            {'title': t['book_title'], 'quantity': t['quantity']}
            for t in related_transactions
        ]

        # Create the transaction dictionary for PreviewTransactionForm
        preview_transaction = {
            'id': transaction_id,
            'borrower': selected_transaction.get('borrower', 'N/A'),
            'date': selected_transaction.get('date', 'N/A'),
            'action': selected_transaction.get('action', 'Borrowed'),
            'due_date': selected_transaction.get('due_date', 'N/A'),
            'returned_date': selected_transaction.get('returned_date', ''),
            'remarks': selected_transaction.get('remarks', ''),
            'books': books
        }

        # Debug: Print the transaction being passed
        print("Opening NewPreviewTransactionForm with transaction:", preview_transaction)

        # Open the PreviewTransactionForm
        dialog = PreviewTransactionForm(preview_transaction, parent=self)
        if dialog.exec():
            updated_transaction = dialog.get_transaction()
            
            # If the transaction is marked as Returned, update the database
            if updated_transaction['action'] == 'Returned':
                try:
                    success = self.borrow_books.return_book(
                        transaction_id=updated_transaction['id'],
                        librarian_id=self.librarian_id,
                        returned_date=updated_transaction['returned_date'],
                        remarks=updated_transaction.get('remarks', '')
                    )
                    if success:
                        # Refresh transactions and history
                        self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id) or []
                        self.display_transactions()
                        self.display_history()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to update transaction status.")
                except Exception as e:
                    QMessageBox.critical(self, "Database Error", f"Failed to return transaction: {str(e)}")

    def on_transaction_double_click(self, row, column):
        if column == 5:  # Skip if clicking on delete button column
            return
        
        # Get the current filtered transactions (same as display_transactions uses)
        search_term = self.trans_search_edit.text().lower()
        transaction_dict = {}
        for trans in self.transactions:
            if trans.get('action') != 'Borrowed':
                continue
            trans_id = trans.get('id')
            if trans_id not in transaction_dict:
                transaction_dict[trans_id] = {
                    'id': trans_id,
                    'borrower': trans.get('borrower', 'N/A'),
                    'date': trans.get('date', 'N/A'),
                    'due_date': trans.get('due_date', 'N/A'),
                    'action': trans.get('action', 'Borrowed'),
                    'remarks': trans.get('remarks', ''),
                    'books': []
                }

            transaction_dict[trans_id]['books'].append ({
                'title': trans.get('book_title', 'N/A'),
                'quantity': trans.get('quantity', 1)
            })
        active_transactions = list(transaction_dict.values())

        if search_term:
            filtered_transactions = [
                trans for trans in active_transactions
                if search_term in trans['borrower'].lower() or 
                    any(search_term in book['title'].lower() for book in trans['books'])
            ]
        else:
            filtered_transactions = active_transactions
        if row >= len(filtered_transactions):
            print("Error: row index out of range")
            QMessageBox.critical(self, "Error", "Invalid transaction selected.")
            return
        selected_transaction = filtered_transactions[row]
        print(f"Open selected transaction:", selected_transaction)
        self.open_edit_transaction(selected_transaction)

    def return_transaction(self, transaction):
        reply = QMessageBox.question(
            self, 
            "Confirm Return",
            f"Are you sure you want to mark transaction #{transaction['id']} as returned?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                success = self.borrow_books.return_book (
                    transaction_id = transaction['id'],
                    librarian_id = self.librarian_id,
                    returned_date=datetime.now().strftime("%Y-%m-%d")
                )
                if success:
                    self.transactions= self.borrow_books.fetch_all_transactions(self.librarian_id)
                    self.display_transactions()
                    self.display_history()
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to return transaction: {str(e)}")

    def delete_transaction(self, transaction):
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete transaction #{transaction['id']}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                self.borrow_books.db_seeder.delete_table(tableName="BookTransaction", column="TransactionID", value=transaction['id'] )
                QMessageBox.information(self, "Success", f"Transaction {transaction} deleted successfully!")
                self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id)
                self.display_transactions()
                self.display_history()
                
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete transaction: {str(e)}")
   
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

    def on_history_double_click(self, row, column):
        print("History row double-clicked:", row, column)
        # Use the same data as display_history
        sorted_transactions = sorted(self.transactions, key=lambda x: x['date'], reverse=True)
        transaction = sorted_transactions[row]
        dialog = HistoryTransactionPreviewForm(transaction, self)
        dialog.exec()

# To run the app
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication


    app = QApplication(sys.argv)
    window = LibraryTransactionSystem()  
    nav_manager._current_window = window
    window.show()
    sys.exit(app.exec())
