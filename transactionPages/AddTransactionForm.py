from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QWidget, QSizePolicy, QSpinBox, QScrollArea, QFrame, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont
from .transaction_logic import BorrowBooks
from tryDatabase import DatabaseSeeder

class BookSelectionWidget(QWidget):
    """Widget for selecting a book and its quantity"""
    remove_requested = Signal(object)
    
    def __init__(self, books_list, show_remove_button=True, parent=None):
        super().__init__(parent)
        self.books_list = books_list
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10,10,10,10)
        layout.setSpacing(30)
        
        # Number label
        self.number_label = QLabel("1.")
        self.number_label.setStyleSheet("""
            color: #5e3e1f;
            margin-left: 80;
            background: transparent;
            border: none;
        """)
        
        # Book selection
        self.book_combo = QComboBox()
        self.book_combo.addItems(books_list)
        self.book_combo.setFont(QFont("Times New Roman", 12))
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
        
        # Quantity selection
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(10)
        self.quantity_spin.setValue(1)
        self.quantity_spin.setFont(QFont("Times New Roman", 12))
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
        
        # Delete button for Books
        if show_remove_button:
            self.remove_btn = QPushButton("X")
            self.remove_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
            self.remove_btn.setFixedSize(25,25)
            self.remove_btn.setStyleSheet("""
                 QPushButton {
                    margin-right:5px;
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
            self.remove_btn.clicked.connect(lambda: self.remove_requested.emit(self))
        
        # Title label
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

        
        # Qty label
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
        
        layout.addWidget(self.number_label)
        layout.addWidget(title_label)
        layout.addWidget(self.book_combo)
        layout.addWidget(qty_label)
        layout.addWidget(self.quantity_spin)
        if show_remove_button:
            layout.addWidget(self.remove_btn)
        layout.addStretch()
    
    def set_number(self, number):
        self.number_label.setText(f"{number}.")
    
    def get_book(self):
        return self.book_combo.currentText()
    
    def get_quantity(self):
        return self.quantity_spin.value()

class AddTransactionForm(QDialog):
    def __init__(self, librarian_id, parent=None):
        super().__init__(parent)
        self.borrow_books = BorrowBooks()
        self.librarian_id = librarian_id
        self.books_list = self.borrow_books.fetch_books(librarian_id)
        if not self.books_list:
            QMessageBox.warning(self, "Error", "No books available in the library.")
            self.close()
            
        self.book_widgets = []
        
        self.setWindowTitle("Add New Transaction")
        self.setStyleSheet("background-color: #f5f1e6;")
        
        from PySide6.QtCore import Qt
        self.setWindowState(Qt.WindowMaximized)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Outer Form Container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_container.setStyleSheet("""
            background: white;
            border: 2px solid #e8d8bd;
            border-radius: 12px;
        """)
        form_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        # Title Label
        title = QLabel("Transaction Details")
        title.setFont(QFont("Times New Roman", 16, QFont.Bold))
        title.setStyleSheet("color: #5e3e1f;")
        title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(title)

        # Helper to Add Each Row
        def add_form_row(label_text, widget):
            row = QHBoxLayout()
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
                    padding-right: 24px; #spaces for buttons
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

        # Borrower Name
        self.borrower_edit = QLineEdit()
        self.borrower_edit.setPlaceholderText("Enter Borrower Name")
        form_layout.addLayout(add_form_row("Borrower:", self.borrower_edit))

        # Books Section - Give it more space
        books_section = QWidget()
        books_layout = QVBoxLayout(books_section)
        books_layout.setContentsMargins(0, 0, 0, 0)
        
        # Books header with add button
        books_header = QHBoxLayout()
        
        # Books label: centered, no border
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

        # Plus button
        self.add_book_btn = QPushButton("+")
        self.add_book_btn.setFixedSize(40,40)
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

        # Layout: label centered, button right
        books_header.addStretch()
        books_header.addWidget(books_label)
        books_header.addStretch()
        books_header.addWidget(self.add_book_btn)
        
        # Container for book widgets
        self.books_container = QWidget()
        self.books_container_layout = QVBoxLayout(self.books_container)
        self.books_container_layout.setContentsMargins(0,0,0,0)
        self.books_container_layout.setSpacing(15)
        
        # Create the scroll area with increased minimum height
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame) 

        
        books_layout.addLayout(books_header)
        books_layout.addWidget(self.scroll_area)
     
        self.scroll_area.setWidget(self.books_container)
        
        # Add the books section with stretch factor to give it more space
        form_layout.addWidget(books_section, 2)  # Give books section more weight
        
        # Add first book widget by default
        self.add_book_widget(show_remove=False)

        # Borrow Date
        self.borrow_date_edit = QDateEdit(QDate.currentDate())
        self.borrow_date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addLayout(add_form_row("Borrowed Date:", self.borrow_date_edit))

        # Due Date
        self.due_date_edit = QDateEdit(QDate.currentDate().addDays(14))
        self.due_date_edit.setDisplayFormat("yyyy-MM-dd")
        form_layout.addLayout(add_form_row("Due Date:", self.due_date_edit))

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Borrowed", "Returned"])
        form_layout.addLayout(add_form_row("Status:", self.status_combo))

        # Remarks - Make it more compact
        self.remarks_edit = QTextEdit()
        self.remarks_edit.setPlaceholderText("Enter any additional remarks or notes (optional)")
        self.remarks_edit.setMaximumHeight(60)  # Limit the height more strictly
        self.remarks_edit.setMinimumHeight(60)  # Set a fixed height
        form_layout.addLayout(add_form_row("Remarks:", self.remarks_edit))

        # Buttons
        button_row = QHBoxLayout()
        button_row.setSpacing(15)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFont(QFont("Times New Roman", 13, QFont.Bold))
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #white;
                color:#5e3e1f ;
                border-radius: 16px;
                padding: 12px 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #5e3e1f;
                color: white;
            }
        """)
        
        # Add Transaction button
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
        
        button_row.addStretch()
        button_row.addWidget(self.cancel_btn)
        button_row.addWidget(self.add_btn)
        button_row.addStretch()
        form_layout.addLayout(button_row)

        main_layout.addWidget(form_container)

        # Button connections
        self.add_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def add_book_widget(self, show_remove=True):
        """Add a new book selection widget"""
        # If this is not the first widget, always show remove button
        if len(self.book_widgets) > 0:
            show_remove = True
            
        book_widget = BookSelectionWidget(
            self.books_list, 
            show_remove_button=show_remove
        )
        book_widget.remove_requested.connect(self.remove_book_widget)
        book_widget.set_number(len(self.book_widgets) + 1)
        
        self.book_widgets.append(book_widget)
        self.books_container_layout.addWidget(book_widget)
    
        book_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # Para sa delete buttons if maraming books 
        self.update_remove_button_visibility()

    def remove_book_widget(self, widget):
        """Remove a book selection widget"""
        if len(self.book_widgets) > 1:
            self.book_widgets.remove(widget)
            widget.deleteLater()
            self.update_book_numbers()
            self.update_remove_button_visibility()

    def update_book_numbers(self):
        """Update the row numbers after removal"""
        for i, widget in enumerate(self.book_widgets):
            widget.set_number(i + 1)

    def update_remove_button_visibility(self):
        """Show/hide remove buttons based on number of book widgets"""
        show_remove = len(self.book_widgets) > 1
        for widget in self.book_widgets:
            if hasattr(widget, 'remove_btn'):
                if show_remove:
                    widget.remove_btn.show()
                else:
                    widget.remove_btn.hide()

    def get_books_data(self):
        """Get all books and their quantities"""
        books_data = []
        for widget in self.book_widgets:
            books_data.append({
                'book': widget.get_book(),
                'quantity': widget.get_quantity()
            })
        return books_data
    
    def parse_borrower_name(self):
        full_name = self.borrower_edit.text().strip()
        parts = full_name.split()
        if len(parts) < 2:
            return None #invalid format
        if len(parts) >=3 :
            first_name = parts[0]
            last_name = parts[-1]
            middle_name = " ".join(parts[1:-1]) if len(parts) > 2 else ""
            borrower_name = f"{first_name} {middle_name} {last_name}".strip()
        else:
            borrower_name = f"{parts[0]} {parts[1]}"
        print(f"Parsed borrower name: {borrower_name}")
        return borrower_name

    
    def accept(self):
        borrower_name = self.borrower_edit.text().strip()
        if not borrower_name:
            QMessageBox.warning(self, "Input Error", "Please enter the borrower's name.")
            return
                
        books_data = self.get_books_data()
        if not books_data:
            QMessageBox.warning(self, "Input Error", "Please add at least one book.")
            return
            
        # Get all members
        members = self.borrow_books.db_seeder.get_all_records(tableName="Member", id=self.librarian_id)
        
        # Improved member matching that handles middle initials
        member_id = None
        for m in members:
            full_name = f"{m['MemberFN']} {m.get('MemberMI', '')} {m['MemberLN']}".replace("  ", " ").strip()
            if full_name.lower() == borrower_name.lower():
                member_id = m["MemberID"]
                break
        
        if not member_id:
            QMessageBox.warning(self, "Input Error", "Borrower not found in the member list.")
            return
        
        # Verify book availability
        books = self.borrow_books.db_seeder.get_all_records(tableName="Book", id=self.librarian_id)
        book_dict = {book["BookTitle"]: book for book in books}

        for book_data in books_data:
            book_title = book_data["book"]
            quantity = book_data["quantity"]

            if book_title not in book_dict:
                QMessageBox.warning(self, "Input Error", f"Book '{book_title}' not found in the library.")
                return
            if book_dict[book_title]["BookAvailableCopies"] < quantity:
                QMessageBox.warning(self, "Input Error", f"Not enough copies of '{book_title}' available.")
                return
        
        # Create the transaction
        transaction_data = [{
            "TransactionType": "Borrow",
            "BorrowedDate": self.borrow_date_edit.date().toString("yyyy-MM-dd"),
            "Status": self.status_combo.currentText(),
            "Remarks": self.remarks_edit.toPlainText().strip() or None,
            "LibrarianID": self.librarian_id,
            "MemberID": member_id,
        }]

        # Seed the transaction data and get TransactionID
        transaction_id = self.borrow_books.db_seeder.seed_data(
            tableName="BookTransaction",
            data=transaction_data,
            columnOrder=[
                "TransactionType", "BorrowedDate", "Status", "Remarks", 
                "LibrarianID", "MemberID"
            ]
        )

        if not transaction_id:
            QMessageBox.warning(self, "Error", "Failed to create transaction.")
            return
        
        # Add transaction details for each book
        for book_data in books_data:
            book_title = book_data["book"]
            quantity = book_data["quantity"]
            book_code = book_dict[book_title]["BookCode"]

            details_data = [{
                "Quantity": quantity,
                "TransactionID": transaction_id,
                "BookCode": book_code,
            }]
            
            self.borrow_books.db_seeder.seed_data(
                tableName="TransactionDetails",
                data=details_data,
                columnOrder=["Quantity", "TransactionID", "BookCode"]
            )
            
            # Update book availability
            self.borrow_books.db_seeder.update_table(
                tableName="Book",
                updates={"BookAvailableCopies": book_dict[book_title]["BookAvailableCopies"] - quantity},
                column="BookCode",
                value=book_code
            )

        QMessageBox.information(self, "Success", "Transaction added successfully.")
        super().accept()  # Close the dialog with Accepted status

    def get_transaction_data(self):
        borrower_name = self.parse_borrower_name()
        if not borrower_name:
            return None
        return {
            "borrower_name": borrower_name,
            "books_data": self.get_books_data(),
            "borrow_date": self.borrow_date_edit.toString("yyyy-MM-dd"),
            "remarks": self.remarks_edit,
            "due_date": self.due_date_edit.toString("yyyy-MM-dd"),
            "status": self.status_combo.currentText()
        }

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    books = ["1984", "To Kill a Mockingbird", "Pride and Prejudice"]
    dialog = AddTransactionForm(books)
    result = dialog.exec()
    
    if result == QDialog.Accepted:
        print("Transaction Added:")
        print("Borrower:", dialog.borrower_edit.text())
        print("Books borrowed:")
        for book_data in dialog.get_books_data():
            print(f"  - {book_data['book']}: {book_data['quantity']} copies")
        print("Borrowed:", dialog.borrow_date_edit.date().toString("yyyy-MM-dd"))
        print("Due:", dialog.due_date_edit.date().toString("yyyy-MM-dd"))
        print("Status:", dialog.status_combo.currentText())
        print("Remarks:", dialog.get_remarks() or "None")
    else:
        print("Transaction cancelled by user")
    # IMPORTANT: Pass the actual librarian_id from navbar_logic or parent window here
    # Example: dialog = AddTransactionForm(librarian_id=passed_librarian_id)
    # For demo/testing, uncomment and set a real librarian_id if needed
    # librarian_id = ...
    # dialog = AddTransactionForm(librarian_id=librarian_id)
    print("This form requires librarian_id to be passed from the navigation logic.")
    # Remove or update this block in production usage.