# Import necessary Qt modules
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLabel, QLineEdit,
    QDateEdit, QCheckBox, QPushButton, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QHeaderView, QTextEdit
)
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont

class PreviewTransactionForm(QDialog):
    """Dialog for previewing and updating transaction details"""
    def __init__(self, transaction, parent=None):
        super().__init__(parent)
        # Set dialog properties
        self.setWindowTitle("Preview Current Transaction")
        self.setFixedSize(1000, 600)  # Fixed size with increased height for remarks
        self.transaction = transaction  # Store the transaction data

        # Apply custom styling to the dialog and its widgets
        self.setStyleSheet("""
            /* Main dialog background */
            QDialog {
                background-color: #f5f1e6;  /* Light beige background */
            }
            /* Label styling */
            QLabel {
                color: #5e3e1f;  /* Dark brown text */
                font-family: 'Times New Roman';
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
            /* Input field styling */
            QLineEdit, QDateEdit, QSpinBox, QTextEdit {
                padding: 8px;
                border: 2px solid #e8d8bd;  /* Light brown border */
                border-radius: 8px;
                background-color: white;
                color: #4a3a28;  /* Medium brown text */
                font-family: 'Times New Roman';
                font-size: 12px;
            }
            /* Focus state for input fields */
            QLineEdit:focus, QDateEdit:focus, QSpinBox:focus, QTextEdit:focus {
                border-color: #5e3e1f;  /* Darker brown when focused */
            }
            /* Button styling */
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                font-family: 'Times New Roman';
                font-size: 12px;
                font-weight: bold;
                color: #5e3e1f;  /* Dark brown text */
                background-color: white;  /* White background */
                border: 2px solid #e8d8bd;  /* Light brown border */
            }
            /* Disabled button styling */
            QPushButton:disabled {
                color: #b8b8b8;  /* Gray text */
            }
            /* Table widget styling */
            QTableWidget {
                background-color: white;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                gridline-color: #e8d8bd;
                color: #4a3a28;
                font-family: 'Times New Roman';
                font-size: 12px;
            }
            /* Table cell styling */
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e8d8bd;
            }
            /* Selected table cell styling */
            QTableWidget::item:selected {
                background-color: #d8c0a0;  /* Light brown selection */
                color: #000000;
            }
            /* Table header styling */
            QHeaderView::section {
                background-color: #e8d8bd;  /* Light brown header */
                color: #5e3e1f;
                font-weight: bold;
                padding: 8px;
                border: none;
            }
            /* Hide date edit dropdown arrow */
            QDateEdit::drop-down { width: 0px; }
            QDateEdit::down-arrow { width: 0px; height: 0px; }
            /* Hide spin box buttons */
            QSpinBox::up-button, QSpinBox::down-button { width: 0px; height: 0px; }
        """)

        # Main layout for the dialog
        layout = QVBoxLayout(self)
        
        # Form layout for transaction details
        form = QFormLayout()
        form.setSpacing(12)  # Spacing between form rows

        # Borrower's Name field
        self.borrower_edit = QLineEdit(transaction.get('borrower', ''))
        self.borrower_edit.setReadOnly(True)  # Make field read-only
        form.addRow("Borrower:", self.borrower_edit)

        # Borrowed Date field
        self.borrowed_date = QDateEdit()
        self.borrowed_date.setDate(QDate.fromString(transaction.get('date', ''), "yyyy-MM-dd"))
        self.borrowed_date.setCalendarPopup(True)  # Enable calendar popup
        self.borrowed_date.setReadOnly(True)  # Make field read-only
        form.addRow("Borrowed Date:", self.borrowed_date)

        # Remarks field
        remarks = transaction.get('remarks') or ""    
        self.remarks_edit = QTextEdit(remarks)
        self.remarks_edit.setReadOnly(True)
        self.remarks_edit.setMaximumHeight(80)  # Limit height
        form.addRow("Remarks:", self.remarks_edit)

        # Add form to main layout
        layout.addLayout(form)

        # Create and setup books table
        self.books_table = QTableWidget()
        self.setup_books_table()
        layout.addWidget(self.books_table)

        # Create return status section
        self.create_return_section(layout)

        # Create dialog buttons
        self.create_buttons(layout)

    def setup_books_table(self):
        """Configure and populate the books table"""
        # Handle both single book and multiple books formats
        books = []
        
        if 'books' in self.transaction and isinstance(self.transaction['books'], list):
            # Multiple books format: list of book dictionaries
            books = self.transaction['books']
        elif 'book_title' in self.transaction:
            # Single book format: convert to list format
            books = [{
                'title': self.transaction.get('book_title', ''),
                'quantity': self.transaction.get('quantity', 1)
            }]
        
        # Configure table dimensions
        self.books_table.setRowCount(len(books))
        self.books_table.setColumnCount(2)
        self.books_table.setHorizontalHeaderLabels(["Book Title", "Quantity"])
        
        # Make table read-only and set selection behavior
        self.books_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.books_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.books_table.verticalHeader().setVisible(False)  # Hide row numbers
        
        # Populate table with book data
        for row, book in enumerate(books):
            title_item = QTableWidgetItem(str(book.get('title', '')))
            quantity_item = QTableWidgetItem(str(book.get('quantity', 1)))
            
            self.books_table.setItem(row, 0, title_item)
            self.books_table.setItem(row, 1, quantity_item)
        
        # Set column widths
        header = self.books_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Stretch title column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Fit quantity column

    def create_return_section(self, layout):
        """Create the return status section with checkbox and date"""
        # Determine if this is a single book transaction
        is_single_book = self.is_single_book()
        
        # Create horizontal layout for return controls
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        # Create checkbox with appropriate text
        checkbox_text = "Book returned" if is_single_book else "All books returned"
        self.returned_checkbox = QCheckBox(checkbox_text)
        
        # Set initial checkbox state based on transaction status
        is_returned = self.transaction.get('action', '') == 'Returned'
        self.returned_checkbox.setChecked(is_returned)
        self.returned_checkbox.stateChanged.connect(self.toggle_returned_date)  # Connect signal
        
        # Custom checkbox styling
        self.returned_checkbox.setStyleSheet("""
            QCheckBox {
                color: #5e3e1f;  /* Dark brown text */
                font-weight: bold;
                spacing: 8px;  /* Space between checkbox and text */
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #e8d8bd;  /* Light brown border */
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #5e3e1f;  /* Dark brown when checked */
                border-color: #5e3e1f;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #a0522d;  /* Lighter brown on hover */
            }
        """)
        
        # Add checkbox to layout with stretchable space
        bottom_layout.addWidget(self.returned_checkbox)
        bottom_layout.addStretch()

        # Create return date label and field
        return_label = QLabel("Return Date:")
        return_label.setStyleSheet("color: #5e3e1f; font-weight: bold;")
        
        self.returned_date = QDateEdit()
        self.returned_date.setCalendarPopup(True)  # Enable calendar popup
        # Set initial date from transaction or current date
        if self.transaction.get('returned_date'):
            self.returned_date.setDate(QDate.fromString(self.transaction['returned_date'], "yyyy-MM-dd"))
        else:
            self.returned_date.setDate(QDate.currentDate())
        
        # Enable/disable date field based on checkbox state
        self.returned_date.setEnabled(is_returned)
        
        # Add date controls to layout
        bottom_layout.addWidget(return_label)
        bottom_layout.addWidget(self.returned_date)

        # Add return section to main layout
        layout.addLayout(bottom_layout)

    def create_buttons(self, layout):
        """Create and configure dialog buttons"""
        # Button layout with horizontal alignment
        btn_layout = QHBoxLayout()
        
        # Save button
        save_btn = QPushButton("Save")
        save_btn.setFont(QFont("Times New Roman", 13, QFont.Bold))
        # Custom styling for save button
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5e3e1f;  /* Dark brown background */
                color: white;  /* White text */
                border-radius: 16px;
                padding: 12px 30px;
                border: 2px solid #5e3e1f;
                max-width: 100px;
                max-height: 10px;
            }
            QPushButton:hover {
                background-color: #a0522d;  /* Lighter brown on hover */
            }
        """)
        save_btn.clicked.connect(self.save_and_close)  # Connect click handler
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Times New Roman", 13, QFont.Bold))
        # Custom styling for cancel button
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;  /* White background */
                color: #5e3e1f;  /* Dark brown text */
                border-radius: 16px;
                padding: 12px 30px;
                border: 2px solid #5e3e1f;  
                max-width: 100px;
                max-height: 10px;
            }
            QPushButton:hover {
                background-color: #e8d8bd;  /* Light brown on hover */
            }
        """)
        cancel_btn.clicked.connect(self.reject)  # Connect to reject (close dialog)
        
        # Add buttons to layout with stretchable space
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def is_single_book(self):
        """Determine if this transaction involves a single book"""
        if 'books' in self.transaction and isinstance(self.transaction['books'], list):
            # Check if there's only one book with quantity 1
            if len(self.transaction['books']) == 1:
                return self.transaction['books'][0].get('quantity', 1) == 1
            return False
        elif 'book_title' in self.transaction:
            # Single book format - check quantity
            return self.transaction.get('quantity', 1) == 1
        return True  # Default to single book if format not recognized

    def toggle_returned_date(self, state):
        """Enable/disable return date field based on checkbox state"""
        self.returned_date.setEnabled(state == 2)  # 2 = checked, 0 = unchecked

    def save_and_close(self):
        """Update transaction data and close dialog with accept"""
        # Update transaction status based on checkbox
        if self.returned_checkbox.isChecked():
            self.transaction['action'] = 'Returned'
            self.transaction['returned_date'] = self.returned_date.date().toString("yyyy-MM-dd")
        else:
            self.transaction['action'] = 'Borrowed'
            self.transaction['returned_date'] = ''
        self.accept()  # Close dialog with success

    def get_transaction(self):
        """Return the updated transaction data"""
        return self.transaction

# Main entry point for testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # Example transaction data for testing - Multiple books format
    transaction_multiple = {
        "borrower": "John Doe",
        "date": "2025-06-19",
        "action": "Borrowed",
        "returned_date": "",
        "remarks": "Student needs these books for research project. Handle with care.",
        "books": [
            {"title": "Sample Book 1", "quantity": 2},
            {"title": "Sample Book 2", "quantity": 1},
            {"title": "Sample Book 3", "quantity": 3}
        ]
    }
    
    # Example transaction data - Single book format (no remarks)
    transaction_single = {
        "borrower": "Jane Smith",
        "book_title": "Single Sample Book",
        "quantity": 1,
        "date": "2025-06-19",
        "action": "Borrowed",
        "returned_date": ""
    }

    # Example with single book but quantity > 1
    transaction_single_multiple_copies = {
        "borrower": "Bob Johnson",
        "book_title": "Popular Textbook",
        "quantity": 3,
        "date": "2025-06-19",
        "action": "Borrowed",
        "returned_date": "",
        "remarks": "Borrowed 3 copies for group study"
    }

    # Create application instance
    app = QApplication(sys.argv)
    
    # Test with multiple books (will show "All books returned")
    dialog = PreviewTransactionForm(transaction_multiple)
    result = dialog.exec()
    
    # Test with single book (will show "Book returned")
    if result:
        dialog2 = PreviewTransactionForm(transaction_single)
        dialog2.exec()