import sys
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QFormLayout, QLineEdit, QTableWidget,
    QTableWidgetItem, QDateEdit, QHeaderView, QTextEdit
)
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont
from .transaction_logic import BorrowBooks
from tryDatabase import DatabaseSeeder
from datetime import datetime, timedelta

class HistoryTransactionPreviewForm(QDialog):
    def __init__(self, transaction, librarian_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("History Preview Transaction")
        self.setFixedSize(1000, 600)  # fixed height 
        self.transaction = transaction
        self.librarian_id = librarian_id
        self.db_seeder=DatabaseSeeder() #for database access 
        
        #fetch transaction by TransactionID
        transaction_id = transaction.get('id')
        if transaction_id:
            self.transaction = self.fetch_transaction_by_id(transaction_id)
        else:
            self.transaction = transaction #fallback to passed transaction

        #apply custom stylign to the dialog and its widgets
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f1e6;
            }
            QLabel {
                color: #5e3e1f;
                font-family: 'Times New Roman';
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
            QLineEdit, QDateEdit, QTextEdit {
                padding: 8px;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                background-color: white;
                color: #4a3a28;
                font-family: 'Times New Roman';
                font-size: 12px;
            }
            QLineEdit:read-only, QDateEdit:read-only, QTextEdit:read-only {
                background-color: white;
                color: #4a3a28;
            }
            QTableWidget {
                background-color: white;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                gridline-color: #e8d8bd;
                color: #4a3a28;
                font-family: 'Times New Roman';
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e8d8bd;
                color: #4a3a28;
                background-color: white;
            }
            QTableWidget::item:selected {
                background-color: #d8c0a0;
                color: #000000;
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
                border: 2px solid #e8d8bd;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #5e3e1f;
                border-color: #5e3e1f;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
                border: 2px solid #e8d8bd;
                border-radius: 4px;
            }
            QCheckBox:disabled {
                color: #5e3e1f;
            }
            /* Hide drop-down arrow in QDateEdit */
            QDateEdit::drop-down { width: 0px; }
            QDateEdit::down-arrow { width: 0px; height: 0px; }
        """)

        #main layout for the dialog
        layout = QVBoxLayout(self)
        
        # for the form layout for transaction details
        form = QFormLayout()
        form.setSpacing(12) #spacing between form rows

        # Borrower's Name filed
        borrower_edit = QLineEdit(self.transaction.get('borrower', ''))
        borrower_edit.setReadOnly(True) # read only field
        form.addRow("Borrower:", borrower_edit)

        # Borrowed Date
        borrowed_date = QDateEdit()
        borrowed_date.setDate(QDate.fromString(self.transaction.get('date', ''), "yyyy-MM-dd"))
        borrowed_date.setCalendarPopup(True) #enable calendar popup
        borrowed_date.setReadOnly(True) #read only field
        form.addRow("Borrowed Date:", borrowed_date)

        # transaction remarks field
        remarks_edit = QTextEdit()
        remarks_edit.setReadOnly(True) #read only field
        if self.transaction.get('remarks'): #get remarks from transaction
            remarks_edit.setPlainText(self.transaction['remarks'])
        else:
            remarks_edit.setPlainText("No remarks available")
        remarks_edit.setMaximumHeight(80)  # Limit height
        form.addRow("Remarks:", remarks_edit)

        # Return Date (moved to left side, no checkbox)
        returned_date = QDateEdit()
        returned_date.setCalendarPopup(True)
        if self.transaction.get('returned_date'):
            returned_date.setDate(QDate.fromString(self.transaction['returned_date'], "yyyy-MM-dd"))
        else:
            returned_date.setDate(QDate.currentDate()) #default to current date
        returned_date.setReadOnly(True)  # Make it read-only
        form.addRow("Returned Date:", returned_date)

        layout.addLayout(form) #add form to main layout

        #create and setup book table
        books_table = QTableWidget()
        self.setup_books_table(books_table)
        layout.addWidget(books_table) #add table to main layout

    #FETCH COMPLETE TRANSACTION WTH DETAILS FROM DATABASE
    def fetch_transaction_by_id(self, transaction_id):
        #get all transactions with details from database
        transactions = self.db_seeder.get_transaction_with_details(librarian_id = self.librarian_id)
        #filter transactions with matching id
        trans_records = [t for t in transactions if t['TransactionID']== transaction_id]
        if not trans_records:
            print(f"No transaction Records found for TransactionID {transaction_id}")
            return {} #return empty dict if not found
        #use first record for basic transaction info
        first_trans = trans_records[0]
        #extract book details from all records
        books = [
            {
                'title': trans['BookTitle'],
                'quantity': trans["Quantity"]
            }
            for trans in trans_records
        ]
        #build complete transaction dict
        transaction = {
            'id': first_trans['TransactionID'],
            'borrower': first_trans['borrower'],
            'date': first_trans['BorrowedDate'],
            'returned_date': first_trans['ReturnedDate'] or '', #handle none
            'action': first_trans['Status'],
            'remarks': first_trans['Remarks'] or '', #handle none
            #get due date
            'due_date': trans_records[0].get("DueDate", "") if trans_records else "",
            'books': books #list of book dictionaries
        }
        return transaction
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
        
        #configure table dimensions
        books_table.setRowCount(len(books))
        books_table.setColumnCount(2)
        books_table.setHorizontalHeaderLabels(["Book Title", "Quantity"])
        
        # Make table completely read-only
        books_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        books_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        books_table.verticalHeader().setVisible(False) #hide row numbers
        
        # Populate table
        for row, book in enumerate(books):
            title_item = QTableWidgetItem(str(book.get('title', '')))
            quantity_item = QTableWidgetItem(str(book.get('quantity', 1)))
            
            books_table.setItem(row, 0, title_item)
            books_table.setItem(row, 1, quantity_item)
        
        # Adjust column widths
        header = books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) #stretch title column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents) #fit quantity column

# Example usage and test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Sample transaction data for testing
    sample_transaction = {
        'borrower': 'John Doe',
        'date': '2024-01-15',
        'returned_date': '2024-01-22',
        'remarks': 'Hello Nads!! ',
        'books': [
            {'title': 'Python Programming', 'quantity': 2},
            {'title': 'Data Structures', 'quantity': 1},
            {'title': 'Algorithms', 'quantity': 3}
        ]
    }
    
    # Create and show the dialog
    dialog = HistoryTransactionPreviewForm(sample_transaction)
    dialog.show()
    
    sys.exit(app.exec())