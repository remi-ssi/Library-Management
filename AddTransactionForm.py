from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QWidget, QSizePolicy, QSpinBox, QScrollArea, QFrame
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

class BookSelectionWidget(QWidget):
    """Widget for selecting a book and its quantity"""
    remove_requested = Signal(object)
    
    def __init__(self, books_list, show_remove_button=True, parent=None):
        super().__init__(parent)
        self.books_list = books_list
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Number label
        self.number_label = QLabel("1.")
        self.number_label.setStyleSheet("""
            color: #5e3e1f;
            margin-left: 5px;
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
    def __init__(self, books_list, parent=None):
        super().__init__(parent)
        self.books_list = books_list
        self.book_widgets = []
        
        self.setWindowTitle("Add New Transaction")
        self.setStyleSheet("background-color: #f5f1e6;")
        self.setMinimumWidth(1200)
        self.showMaximized()  # Maximized window - keeps title bar and system buttons

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
        form_container.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

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
                QLineEdit, QComboBox, QDateEdit {
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
                    padding-right: 24px; /* Make space for the buttons */
                }

                QDateEdit::up-button, QDateEdit::down-button {
                    width: 0px;
                    height: 0px;
                    border: none;
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

        # Books Section
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
        self.add_book_btn.setFixedSize(30,30)
        self.add_book_btn.setStyleSheet("""
            QPushButton {
                margin-top:5px;
                margin-right:5px;
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
        self.books_container_layout.setContentsMargins(0, 0, 0, 0)
        self.books_container_layout.setSpacing(10)
        
        # Create the scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame) 
        self.scroll_area.setMaximumHeight(800)  

        
        books_layout.addLayout(books_header)
        books_layout.addWidget(self.scroll_area)
     
        self.scroll_area.setWidget(self.books_container)
        
        form_layout.addWidget(books_section)
        
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

        # Buttons
        button_row = QHBoxLayout()
        self.add_btn = QPushButton("Add Transaction")
        self.add_btn.setFont(QFont("Times New Roman", 13, QFont.Bold))
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5e3e1f;
                color: white;
                border-radius: 16px;
                padding: 12px 30px;
            }
            QPushButton:hover {
                background-color: #a0522d;
            }
        """)
        button_row.addStretch()
        button_row.addWidget(self.add_btn)
        button_row.addStretch()
        form_layout.addLayout(button_row)

        main_layout.addWidget(form_container)

        # Behavior
        self.add_btn.clicked.connect(self.accept)

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

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    books = ["1984", "To Kill a Mockingbird", "Pride and Prejudice"]
    dialog = AddTransactionForm(books)
    if dialog.exec():
        print("Borrower:", dialog.borrower_edit.text())
        print("Books borrowed:")
        for book_data in dialog.get_books_data():
            print(f"  - {book_data['book']}: {book_data['quantity']} copies")
        print("Borrowed:", dialog.borrow_date_edit.date().toString("yyyy-MM-dd"))
        print("Due:", dialog.due_date_edit.date().toString("yyyy-MM-dd"))
        print("Status:", dialog.status_combo.currentText())