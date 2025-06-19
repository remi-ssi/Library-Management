from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QTableWidget,
    QTableWidgetItem, QDateEdit, QCheckBox, QPushButton, QHBoxLayout, QHeaderView
)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont

class HistoryTransactionPreviewForm(QDialog):
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
            QLineEdit, QDateEdit {
                padding: 8px;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                background-color: #f5f3ed;
                color: #5e3e1f;
                font-family: 'Times New Roman';
                font-size: 12px;
            }
            QLineEdit:read-only, QDateEdit:read-only {
                background-color: #f5f3ed;
                color: #5e3e1f;
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
                color: #5e3e1f;
                background-color: #f5f3ed;
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
                font-family: 'Times New Roman';
            }
            QCheckBox {
                color: #5e3e1f;
                font-family: 'Times New Roman';
                font-size: 12px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:checked {
                background-color: #27ae60;
                border: 2px solid #27ae60;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #f5f3ed;
                border: 2px solid #e8d8bd;
                border-radius: 3px;
            }
            QCheckBox:disabled {
                color: #5e3e1f;
            }
            /* Hide drop-down arrow in QDateEdit */
            QDateEdit::drop-down { width: 0px; }
            QDateEdit::down-arrow { width: 0px; height: 0px; }
        """)

        layout = QVBoxLayout(self)
        
        # Basic transaction info
        form = QFormLayout()
        form.setSpacing(12)

        # Borrower's Name
        borrower_edit = QLineEdit(self.transaction.get('borrower', ''))
        borrower_edit.setReadOnly(True)
        form.addRow("Borrower:", borrower_edit)

        # Borrowed Date
        borrowed_date = QDateEdit()
        borrowed_date.setDate(QDate.fromString(self.transaction.get('date', ''), "yyyy-MM-dd"))
        borrowed_date.setCalendarPopup(True)
        borrowed_date.setReadOnly(True)
        form.addRow("Borrowed Date:", borrowed_date)

        layout.addLayout(form)

        books_table = QTableWidget()
        self.setup_books_table(books_table)
        layout.addWidget(books_table)

        # Return Date (moved to left side, no checkbox)
        returned_date = QDateEdit()
        returned_date.setCalendarPopup(True)
        if self.transaction.get('returned_date'):
            returned_date.setDate(QDate.fromString(self.transaction['returned_date'], "yyyy-MM-dd"))
        else:
            returned_date.setDate(QDate.currentDate())
        returned_date.setReadOnly(True)  # Make it read-only
        form.addRow("Returned Date:", returned_date)

        

    def setup_books_table(self, books_table):
        # Handle both single book and multiple books formats (same as the working form)
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
        
        books_table.setRowCount(len(books))
        books_table.setColumnCount(2)
        books_table.setHorizontalHeaderLabels(["Book Title", "Quantity"])
        
        # Make table completely read-only
        books_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        books_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        books_table.verticalHeader().setVisible(False)
        
        # Populate table
        for row, book in enumerate(books):
            title_item = QTableWidgetItem(str(book.get('title', '')))
            quantity_item = QTableWidgetItem(str(book.get('quantity', 1)))
            
            books_table.setItem(row, 0, title_item)
            books_table.setItem(row, 1, quantity_item)
        
        # Adjust column widths
        header = books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)