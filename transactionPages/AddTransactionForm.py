# Import necessary Qt modules and other dependencies
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QWidget, QSizePolicy, QSpinBox, QScrollArea, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from .transaction_logic import BorrowBooks
from datetime import datetime
import sqlite3

class BookSelectionWidget(QWidget):
    """Custom widget for selecting a book and its quantity in the transaction form"""
    # Signal emitted when remove button is clicked
    remove_requested = Signal(object)
    
    def __init__(self, books_list, show_remove_button=True, parent=None):
        super().__init__(parent)
        self.books_list = books_list  # List of available books
        
        # Set up horizontal layout for the widget
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(30)
        
        # Number label to show book position (1., 2., etc.)
        self.number_label = QLabel("1.")
        self.number_label.setStyleSheet("""
            color: #5e3e1f;
            margin-left: 80;
            background: transparent;
            border: none;
        """)
        
        # Combo box for book selection
        self.book_combo = QComboBox()
        self.book_combo.addItems(books_list)  # Populate with available books
        self.book_combo.setFont(QFont("Times New Roman", 12))
        # Custom styling for the combo box
        self.book_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #e8d8bd;
                border-radius: 16px;
                padding: 8px 14px;
                background: white;
                color: #4a3a28;
                min-width: 200px;
            }
            QComboBox QAbstractItemView {
                background: #fffaf2;
                color: #4a3a28;
                selection-background-color: #d8c0a0;
                selection-color: #000000;
                border: 1px solid #e8d8bd;
            }
            QComboBox::item {
                padding: 6px 10px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #e8d8bd;
                background: #f8f8f8;
                border-top-right-radius: 14px;
                border-bottom-right-radius: 14px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #4a3a28;
                width: 0;
                height: 0;
            }
        """)
        
        # Spin box for quantity selection
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)  # Minimum quantity
        self.quantity_spin.setMaximum(10)  # Maximum quantity
        self.quantity_spin.setValue(1)  # Default quantity
        self.quantity_spin.setFont(QFont("Times New Roman", 12))
        # Custom styling for the spin box
        self.quantity_spin.setStyleSheet("""
            QSpinBox {
                border: 2px solid #e8d8bd;
                border-radius: 16px;
                padding: 8px 14px;
                background: white;
                color: #4a3a28;
                min-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                subcontrol-origin: border;
                width: 20px;
                border-left: 1px solid #e8d8bd;
                background: #f8f8f8;
            }
            QSpinBox::up-button {
                subcontrol-position: top right;
                border-top-right-radius: 14px;
            }
            QSpinBox::down-button {
                subcontrol-position: bottom right;
                border-bottom-right-radius: 14px;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-bottom: 4px solid #4a3a28;
                width: 0;
                height: 0;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 3px solid transparent;
                border-right: 3px solid transparent;
                border-top: 4px solid #4a3a28;
                width: 0;
                height: 0;
            }
        """)
        
        # Remove button (only shown when needed)
        if show_remove_button:
            self.remove_btn = QPushButton("X")
            self.remove_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
            self.remove_btn.setFixedSize(25, 25)
            # Custom styling for remove button
            self.remove_btn.setStyleSheet("""
                QPushButton {
                    margin-right: 5px;
                    color: #dc3545;
                    font-size: 15px;
                    font-weight: bold;
                    background-color: #fff;
                    border: 2px solid #e8d8bd;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #dc3545;
                    color: #fff;
                }
            """)
            # Connect button click to remove signal
            self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        
        # Title label for book selection
        title_label = QLabel("Title:")
        title_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: #5e3e1f;
                border: 2px solid #e8d8bd;
                border-radius: 12px;
                padding: 4px 8px;
                background-color: white;
                min-width: 40px;
            }
        """)
        
        # Quantity label
        qty_label = QLabel("Qty:")
        qty_label.setFont(QFont("Times New Roman", 11, QFont.Bold))
        qty_label.setStyleSheet("""
            QLabel {
                color: #5e3e1f;
                border: 2px solid #e8d8bd;
                border-radius: 12px;
                padding: 4px 8px;
                background-color: white;
                min-width: 30px;
            }
        """)
        
        # Add all widgets to the layout
        layout.addWidget(self.number_label)
        layout.addWidget(title_label)
        layout.addWidget(self.book_combo)
        layout.addWidget(qty_label)
        layout.addWidget(self.quantity_spin)
        if show_remove_button:
            layout.addWidget(self.remove_btn)
        layout.addStretch()  # Add stretchable space
    
    def set_number(self, number):
        """Update the position number label"""
        self.number_label.setText(f"{number}.")
    
    def get_book(self):
        """Get the currently selected book title"""
        return self.book_combo.currentText()
    
    def get_quantity(self):
        """Get the currently selected quantity"""
        return self.quantity_spin.value()

class AddTransactionForm(QDialog):
    """Dialog for adding new book transactions"""
    def __init__(self, librarian_id, parent=None):
        super().__init__(parent)
        # Initialize transaction logic handler
        self.borrow_books = BorrowBooks()
        self.librarian_id = librarian_id
        # Fetch available books from database
        self.books_list = self.borrow_books.fetch_books(librarian_id)
        if not self.books_list:
            QMessageBox.warning(self, "Error", "No books available in the library.")
            self.close()
        
        # List to store book selection widgets
        self.book_widgets = []
        
        # Set dialog properties
        self.setWindowTitle("Add New Transaction")
        self.setStyleSheet("background-color: #f5f1e6;")  # Light beige background
        self.setWindowState(Qt.WindowMaximized)  # Start maximized

        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Form container widget
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        # Styling for form container
        form_container.setStyleSheet("""
            background: white;
            border: 2px solid #e8d8bd;
            border-radius: 12px;
        """)
        form_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Set form layout margins and spacing
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        # Title label for the form
        title = QLabel("Transaction Details")
        title.setFont(QFont("Times New Roman", 16, QFont.Bold))
        title.setStyleSheet("color: #5e3e1f;")  # Dark brown text
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        # Helper function to create consistent form rows
        def add_form_row(label_text, widget):
            """Helper to create a labeled form row with consistent styling"""
            row = QHBoxLayout()
            # Create label with consistent styling
            label = QLabel(f"{label_text}")
            label.setFont(QFont("Times New Roman", 12, QFont.Bold))
            label.setFixedWidth(140)
            label.setStyleSheet("""
                QLabel {
                    color: #5e3e1f;
                    border: 2px solid #e8d8bd;
                    border-radius: 16px;
                    padding: 6px 12px;
                    background-color: white;
                }
            """)
            # Apply consistent styling to input widgets
            widget.setFont(QFont("Times New Roman", 12))
            widget.setStyleSheet("""
                QLineEdit, QComboBox, QDateEdit, QTextEdit {
                    border: 2px solid #e8d8bd;
                    border-radius: 16px;
                    padding: 8px 14px;
                    background: white;
                    color: #4a3a28;
                }
                QComboBox QAbstractItemView {
                    background: #fffaf2;
                    color: #4a3a28;
                    selection-background-color: #d8c0a0;
                    selection-color: #000000;
                    border: 1px solid #e8d8bd;
                }
                QComboBox::item {
                    padding: 6px 10px;
                }
                QComboBox::drop-down {
                    border: none;
                }
                QDateEdit {
                    padding-right: 24px;
                }
                QDateEdit::up-button, QDateEdit::down-button {
                    width: 0px;
                    height: 0px;
                    border: none;
                }
                QTextEdit {
                    min-height: 60px;
                    max-height: 80px;
                }
            """)
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            row.addWidget(label)
            row.addWidget(widget)
            return row

        # Member ID input field
        self.member_id_edit = QLineEdit()
        self.member_id_edit.setPlaceholderText("Enter Member ID")
        form_layout.addLayout(add_form_row("Member ID:", self.member_id_edit))

        # Borrower name input field
        self.borrower_edit = QLineEdit()
        self.borrower_edit.setPlaceholderText("Enter Borrower Name (e.g., John A. Doe)")
        form_layout.addLayout(add_form_row("Borrower Name:", self.borrower_edit))

        # Books selection section
        books_section = QWidget()
        books_layout = QVBoxLayout(books_section)
        books_layout.setContentsMargins(0, 0, 0, 0)
        
        # Books section header with add button
        books_header = QHBoxLayout()
        books_label = QLabel("Books")
        books_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        books_label.setAlignment(Qt.AlignCenter)
        books_label.setStyleSheet("""
            QLabel {
                color: #5e3e1f;
                border: none;
                background: transparent;
                padding: 6px 12px;
            }
        """)
        # Add book button
        self.add_book_btn = QPushButton("+")
        self.add_book_btn.setFixedSize(40, 40)
        self.add_book_btn.setStyleSheet("""
            QPushButton {
                margin-top:10px;
                margin-right:8px;
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
        self.add_book_btn.clicked.connect(self.add_book_widget)
        books_header.addStretch()
        books_header.addWidget(books_label)
        books_header.addStretch()
        books_header.addWidget(self.add_book_btn)
        
        # Container for book selection widgets
        self.books_container = QWidget()
        self.books_container_layout = QVBoxLayout(self.books_container)
        self.books_container_layout.setContentsMargins(0, 0, 0, 0)
        self.books_container_layout.setSpacing(15)
        
        # Scroll area for books container
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        books_layout.addLayout(books_header)
        books_layout.addWidget(self.scroll_area)
        self.scroll_area.setWidget(self.books_container)
        
        # Add books section to form
        form_layout.addWidget(books_section, 2)  # Stretch factor 2
        
        # Add first book widget (without remove button)
        self.add_book_widget(show_remove=False)

        # Borrow date input
        self.borrow_date_edit = QDateEdit(QDate.currentDate())
        self.borrow_date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addLayout(add_form_row("Borrowed Date:", self.borrow_date_edit))

        # Due date input (default 14 days from today)
        self.due_date_edit = QDateEdit(QDate.currentDate().addDays(14))
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addLayout(add_form_row("Due Date:", self.due_date_edit))

        # Remarks text field
        self.remarks_edit = QTextEdit()
        self.remarks_edit.setPlaceholderText("Enter any additional remarks or notes (optional)")
        self.remarks_edit.setMaximumHeight(60)
        self.remarks_edit.setMinimumHeight(60)
        form_layout.addLayout(add_form_row("Remarks:", self.remarks_edit))

        # Form buttons (Cancel and Add)
        button_row = QHBoxLayout()
        button_row.setSpacing(15)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFont(QFont("Times New Roman", 13, QFont.Bold))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #white;
                color:#5e3e1f;
                border: 2px solid #e8d8bd;
                border-radius: 16px;
                padding: 12px 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5e3e1f;
                color: white;
            }
        """)
        
        # Add transaction button
        self.add_btn = QPushButton("Add Transaction")
        self.add_btn.setFont(QFont("Times New Roman", 13, QFont.Bold))
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5e3e1f;
                color: white;
                border-radius: 16px;
                padding: 12px 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #a0522d;
            }
        """)
        
        # Add buttons to layout with stretchable space
        button_row.addStretch()
        button_row.addWidget(self.cancel_btn)
        button_row.addWidget(self.add_btn)
        button_row.addStretch()
        form_layout.addLayout(button_row)

        # Add form container to main layout
        main_layout.addWidget(form_container)

        # Connect button signals
        self.add_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def add_book_widget(self, show_remove=True):
        """Add a new book selection widget to the form"""
        # Only show remove button if there are existing widgets
        if len(self.book_widgets) > 0:
            show_remove = True
            
        # Create new book selection widget
        book_widget = BookSelectionWidget(
            self.books_list,
            show_remove_button=show_remove
        )
        # Connect remove signal
        book_widget.remove_requested.connect(self.remove_book_widget)
        # Set position number
        book_widget.set_number(len(self.book_widgets) + 1)
        # Add to widgets list and layout
        self.book_widgets.append(book_widget)
        self.books_container_layout.addWidget(book_widget)
        book_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # Update remove button visibility
        self.update_remove_button_visibility()

    def remove_book_widget(self, widget):
        """Remove a book selection widget from the form"""
        # Only remove if we have more than one widget
        if len(self.book_widgets) > 1:
            self.book_widgets.remove(widget)
            widget.deleteLater()  # Clean up widget
            # Update remaining widget numbers
            self.update_book_numbers()
            self.update_remove_button_visibility()

    def update_book_numbers(self):
        """Update the position numbers for all book widgets"""
        for i, widget in enumerate(self.book_widgets):
            widget.set_number(i + 1)

    def update_remove_button_visibility(self):
        """Show/hide remove buttons based on number of widgets"""
        show_remove = len(self.book_widgets) > 1
        for widget in self.book_widgets:
            if hasattr(widget, 'remove_btn'):
                if show_remove:
                    widget.remove_btn.show()
                else:
                    widget.remove_btn.hide()

    def get_books_data(self):
        """Get list of selected books and quantities"""
        books_data = []
        for widget in self.book_widgets:
            books_data.append({
                'book': widget.get_book(),
                'quantity': widget.get_quantity()
            })
        return books_data
    
    def parse_borrower_name(self, member_id, full_name):
        """Validate that member ID matches the provided name"""
        # Get all members from database
        members = self.borrow_books.db_seeder.get_all_records(tableName="Member", id=self.librarian_id)
        # Find member with matching ID
        member = next((m for m in members if m["MemberID"] == int(member_id)), None)
        if not member:
            return None, None
        # Construct expected name format
        expected_name = f"{member['MemberFN']} {member.get('MemberMI', '')} {member['MemberLN']}".replace("  ", " ").strip()
        # Compare names case-insensitively
        if full_name.lower() != expected_name.lower():
            return None, None
        return member_id, expected_name

    def accept(self):
        """Handle form submission and validation"""
        # Get form values
        member_id = self.member_id_edit.text().strip()
        borrower_name = self.borrower_edit.text().strip()
        due_date = self.due_date_edit.date().toString("yyyy-MM-dd")
        borrow_date = self.borrow_date_edit.date().toString("yyyy-MM-dd")

        # Validate member ID
        if not member_id or not member_id.isdigit():
            QMessageBox.warning(self, "Input Error", "Please enter a valid Member ID (numeric).")
            return

        # Validate borrower name
        if not borrower_name:
            QMessageBox.warning(self, "Input Error", "Please enter the borrower's name.")
            return

        # Validate member ID matches borrower name
        validated_member_id, validated_name = self.parse_borrower_name(member_id, borrower_name)
        if not validated_member_id:
            QMessageBox.warning(self, "Input Error", "Member ID does not match the provided borrower name.")
            return

        # Get selected books
        books_data = self.get_books_data()
        if not books_data:
            QMessageBox.warning(self, "Input Error", "Please add at least one book.")
            return

        # Validate due date is after borrow date
        if datetime.strptime(due_date, "%Y-%m-%d") < datetime.strptime(borrow_date, "%Y-%m-%d"):
            QMessageBox.warning(self, "Input Error", "Due date cannot be before borrow date.")
            return
        
        # Verify book availability
        books = self.borrow_books.db_seeder.get_all_records(tableName="Book", id=self.librarian_id)
        book_dict = {book["BookTitle"]: book for book in books}

        for book_data in books_data:
            book_title = book_data["book"]
            quantity = book_data["quantity"]
            # Check book exists
            if book_title not in book_dict:
                QMessageBox.warning(self, "Input Error", f"Book '{book_title}' not found in the library.")
                return
            # Check sufficient copies available
            if book_dict[book_title]["BookAvailableCopies"] < quantity:
                QMessageBox.warning(self, "Input Error", f"Not enough copies of '{book_title}' available.")
                return
        
        # Prepare transaction data for database
        transaction_data = [{
            "BorrowedDate": borrow_date,
            "Status": "Borrowed",  # New transactions are always "Borrowed"
            "Remarks": self.remarks_edit.toPlainText().strip() or None,
            "LibrarianID": self.librarian_id,
            "MemberID": int(validated_member_id),
        }]

        try:
            # Ensure tables exist
            self.borrow_books.db_seeder.create_table("BookTransaction")
            self.borrow_books.db_seeder.create_table("TransactionDetails")
            
            # Insert transaction record
            transaction_id = self.borrow_books.db_seeder.seed_data(
                tableName="BookTransaction",
                data=transaction_data,
                columnOrder=["BorrowedDate", "Status", "Remarks", "LibrarianID", "MemberID"]
            )

            if not transaction_id:
                QMessageBox.warning(self, "Error", "Failed to create transaction. Check database logs for details.")
                print(f"Transaction creation failed: {transaction_data}")
                return
            
            # Add transaction details for each book
            for book_data in books_data:
                book_title = book_data["book"]
                quantity = book_data["quantity"]
                book_code = book_dict[book_title]["BookCode"]

                details_data = [{
                    "Quantity": quantity,
                    "DueDate": due_date,
                    "TransactionID": transaction_id,
                    "BookCode": book_code,
                }]
                
                # Insert transaction detail record
                success = self.borrow_books.db_seeder.seed_data(
                    tableName="TransactionDetails",
                    data=details_data,
                    columnOrder=["Quantity", "DueDate", "TransactionID", "BookCode"]
                )
                
                if not success:
                    QMessageBox.warning(self, "Error", f"Failed to add details for book '{book_title}'.")
                    # Rollback transaction if details fail
                    self.borrow_books.db_seeder.delete_table("BookTransaction", "TransactionID", transaction_id, self.librarian_id)
                    return
                
                # Update book inventory
                self.borrow_books.db_seeder.update_table(
                    tableName="Book",
                    updates={"BookAvailableCopies": book_dict[book_title]["BookAvailableCopies"] - quantity},
                    column="BookCode",
                    value=book_code
                )

            # Show success message
            QMessageBox.information(self, "Success", "Borrow transaction added successfully!")
            
            # Notify parent to refresh if possible
            if self.parent() and hasattr(self.parent(), 'refresh_transaction_displays'):
                print("📢 Notifying parent to refresh displays...")
                self.parent().refresh_transaction_displays()
            
            # Close dialog with success
            super().accept()

        except sqlite3.Error as e:
            # Handle database errors
            QMessageBox.warning(self, "Error", f"Database error: {str(e)}")
            print(f"Transaction creation error: {str(e)}, Data: {transaction_data}")
            # Rollback transaction if error occurs
            if transaction_id:
                self.borrow_books.db_seeder.delete_table("BookTransaction", "TransactionID", transaction_id, self.librarian_id)
            return

    def get_transaction_data(self):
        """Get validated transaction data from form"""
        member_id = self.member_id_edit.text().strip()
        borrower_name = self.borrower_edit.text().strip()
        # Validate member ID and name
        validated_member_id, validated_name = self.parse_borrower_name(member_id, borrower_name)
        if not validated_member_id:
            return None
        # Return structured transaction data
        return {
            "member_id": validated_member_id,
            "borrower_name": validated_name,
            "books_data": self.get_books_data(),
            "borrow_date": self.borrow_date_edit.date().toString("yyyy-MM-dd"),
            "due_date": self.due_date_edit.date().toString("yyyy-MM-dd"),
            "status": "Borrowed",  # Always "Borrowed" for new transactions
            "remarks": self.remarks_edit.toPlainText().strip() or None
        }

# Main entry point for testing
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    # Create application instance
    app = QApplication(sys.argv)
    # Create dialog instance (with dummy librarian_id for testing)
    dialog = AddTransactionForm(librarian_id=1)
    # Show dialog and get result
    result = dialog.exec()
    
    # Print transaction data if accepted
    if result == QDialog.Accepted:
        print("Transaction Added:")
        print("Member ID:", dialog.member_id_edit.text())
        print("Borrower:", dialog.borrower_edit.text())
        print("Books borrowed:")
        for book_data in dialog.get_books_data():
            print(f"  - {book_data['book']}: {book_data['quantity']} copies")
        print("Borrowed:", dialog.borrow_date_edit.date().toString("yyyy-MM-dd"))
        print("Due:", dialog.due_date_edit.date().toString("yyyy-MM-dd"))
        print("Status: Borrowed")  # Always "Borrowed" for new transactions
        print("Remarks:", dialog.remarks_edit.toPlainText() or "None")
    else:
        print("Transaction cancelled by user")