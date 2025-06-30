from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QSpinBox,
    QDateEdit, QCheckBox, QPushButton, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from .transaction_logic import BorrowBooks
from tryDatabase import DatabaseSeeder


class PreviewTransactionForm(QDialog):
    def __init__(self, transaction, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preview Transaction")
        self.setFixedSize(1000, 500)
        self.transaction = transaction

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f3ed;
            }
            QLabel {
                color: #5e3e1f;
                font-family: 'Times New Roman';
                font-size: 14px;
                font-weight: bold;
                background-color:#transparent;
            }
            QLineEdit, QDateEdit, QSpinBox {
                padding: 8px;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                background-color: #f5f3ed;
                color: #5e3e1f;
                font-family: 'Times New Roman';
                font-size: 12px;
            }
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus {
                border-color: #8B4513;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                font-family: 'Times New Roman';
                font-size: 12px;
                font-weight: bold;
                color: #5e3e1f;  /* Set button text color */
                background-color: black; /* Or your preferred color */
            }
            QPushButton:disabled {
                color: #b8b8b8;  /* Optional: gray out disabled buttons */
            }
            QTableWidget {
                background-color: #f5f3ed;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                gridline-color: #e8d8bd;
                color: #5e3e1f;
                font-family: 'Times New Roman';
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e8d8bd;
            }
            QTableWidget::item:selected {
                background-color: #e8d8bd;
            }
            QHeaderView::section {
                background-color: #e8d8bd;
                color: #5e3e1f;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            /* Hide drop-down arrow in QDateEdit */
            QDateEdit::drop-down { width: 0px; }
            QDateEdit::down-arrow { width: 0px; height: 0px; }
            /* Hide spinbox arrows */
            QSpinBox::up-button, QSpinBox::down-button { width: 0px; height: 0px; }
        """)

        layout = QVBoxLayout(self)
        
        # Basic transaction info
        form = QFormLayout()
        form.setSpacing(12)

        # Borrower's Name
        self.borrower_edit = QLineEdit(transaction.get('borrower', ''))
        self.borrower_edit.setReadOnly(True)
        form.addRow("Borrower:", self.borrower_edit)

        # Borrowed Date
        self.borrowed_date = QDateEdit()
        self.borrowed_date.setDate(QDate.fromString(transaction.get('date', ''), "yyyy-MM-dd"))
        self.borrowed_date.setCalendarPopup(True)
        self.borrowed_date.setReadOnly(True)
        form.addRow("Borrowed Date:", self.borrowed_date)

        layout.addLayout(form)

        
        self.books_table = QTableWidget()
        self.setup_books_table()
        layout.addWidget(self.books_table)

        # Returned Checkbox and Date
        returned_layout = QHBoxLayout()
        self.returned_checkbox = QCheckBox("All books returned")
        is_returned = transaction.get('action', '') == 'Returned'
        self.returned_checkbox.setChecked(is_returned)
        self.returned_checkbox.stateChanged.connect(self.toggle_returned_date)
        self.returned_checkbox.setStyleSheet("color: #5e3e1f; font-weight: bold;")

        self.returned_date = QDateEdit()
        self.returned_date.setCalendarPopup(True)
        if transaction.get('returned_date'):
            self.returned_date.setDate(QDate.fromString(transaction['returned_date'], "yyyy-MM-dd"))
        else:
            self.returned_date.setDate(QDate.currentDate())
        self.returned_date.setReadOnly(False)
        self.returned_date.setEnabled(True)

        # Create a horizontal layout for the checkbox and return date
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Left: Checkbox
        self.returned_checkbox = QCheckBox("All books returned")
        self.returned_checkbox.setStyleSheet("color: #5e3e1f; font-weight: bold;")
        bottom_layout.addWidget(self.returned_checkbox)

        # Stretch pushes the next widgets to the right
        bottom_layout.addStretch()

        # Right: Return Date label and field
        return_label = QLabel("Return Date:")
        return_label.setStyleSheet("color: #5e3e1f; font-weight: bold;")
        bottom_layout.addWidget(return_label)
        bottom_layout.addWidget(self.returned_date)

        # Add to main layout
        layout.addLayout(bottom_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setFont(QFont("Times New Roman", 13, QFont.Bold))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5e3e1f;
                color: white;
                border-radius: 16px;
                padding: 12px 30px;
                border: 2px solid #5e3e1f;  /* Add border */
                max-width: 100px;
                max-height:10px;
            }
            QPushButton:hover {
                background-color: #a0522d;
            }
        """)

        save_btn.clicked.connect(self.save_and_close)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Times New Roman", 13, QFont.Bold))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f3ed;
                color: #5e3e1f;
                border-radius: 16px;
                padding: 12px 30px;
                border: 2px solid #5e3e1f;  
                max-width: 100px;
                max-height:10px;
            }
            QPushButton:hover {
                background-color: #e8d8bd;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def setup_books_table(self):
        # Handle both single book and multiple books formats
        books = []
        
        if 'books' in self.transaction and isinstance(self.transaction['books'], list):
            # Multiple books format: transaction = {'borrower': 'John', 'books': [{'title': 'Book1', 'quantity': 2}, ...]}
            books = self.transaction['books']
        elif 'book_title' in self.transaction:
            # Single book format: transaction = {'borrower': 'John', 'book_title': 'Book1', 'quantity': 1}
            books = [{
                'title': self.transaction.get('book_title', ''),
                'quantity': self.transaction.get('quantity', 1)
            }]
        
        self.books_table.setRowCount(len(books))
        self.books_table.setColumnCount(2)
        self.books_table.setHorizontalHeaderLabels(["Book Title", "Quantity"])
        
        # Make table read-only and set up sizing
        self.books_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.books_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.books_table.verticalHeader().setVisible(False)
        
        # Populate table
        for row, book in enumerate(books):
            title_item = QTableWidgetItem(str(book.get('title', '')))
            quantity_item = QTableWidgetItem(str(book.get('quantity', 1)))
            
            self.books_table.setItem(row, 0, title_item)
            self.books_table.setItem(row, 1, quantity_item)
        
        # Adjust column widths
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

    def toggle_returned_date(self, state):
        self.returned_date.setEnabled(state == 2)  # 2 means checked

    def save_and_close(self):
        # Update transaction with returned status and date
        if self.returned_checkbox.isChecked():
            self.transaction['action'] = 'Returned'
            self.transaction['returned_date'] = self.returned_date.date().toString("yyyy-MM-dd")
        else:
            self.transaction['action'] = 'Borrowed'
            self.transaction['returned_date'] = ''
        self.accept()

    def get_transaction(self):
        return self.transaction

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # Example transaction data for testing - Multiple books format
    transaction_multiple = {
        "borrower": "John Doe",
        "date": "2025-06-19",
        "action": "Borrowed",
        "returned_date": "",
        "books": [
            {"title": "Sample Book 1", "quantity": 2},
            {"title": "Sample Book 2", "quantity": 1},
            {"title": "Sample Book 3", "quantity": 3}
        ]
    }
    
    # Example transaction data - Single book format (backward compatibility)
    transaction_single = {
        "borrower": "Jane Smith",
        "book_title": "Single Sample Book",
        "quantity": 1,
        "date": "2025-06-19",
        "action": "Borrowed",
        "returned_date": ""
    }

    app = QApplication(sys.argv)
    
    # Test with multiple books    dialog = PreviewTransactionForm(transaction_multiple)
    dialog.exec()
    