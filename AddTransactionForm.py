from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QDateEdit, QPushButton, QWidget, QSizePolicy  # <-- add QSizePolicy here
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont

class AddTransactionForm(QDialog):
    def __init__(self, books_list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Transaction")
        self.setStyleSheet("background-color: #f5f1e6;")
        self.setMinimumWidth(460)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Outer Form Container
        form_container = QWidget()
        form_container.setStyleSheet("""
            background: white;
            border: 2px solid #e8d8bd;
            border-radius: 12px;
        """)
        form_layout = QVBoxLayout(form_container)
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
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # <-- Add this line
            row.addWidget(label)
            row.addWidget(widget)
            return row

        # Borrower Name
        self.borrower_edit = QLineEdit()
        self.borrower_edit.setPlaceholderText("Enter Borrower Name")
        form_layout.addLayout(add_form_row("Borrower:", self.borrower_edit))

        # Book
        self.book_combo = QComboBox()
        self.book_combo.addItems(books_list)
        form_layout.addLayout(add_form_row("Book:", self.book_combo))

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

if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    books = ["1984", "To Kill a Mockingbird", "Pride and Prejudice"]
    dialog = AddTransactionForm(books)
    if dialog.exec():
        print("Borrower:", dialog.borrower_edit.text())
        print("Book:", dialog.book_combo.currentText())
        print("Borrowed:", dialog.borrow_date_edit.date().toString("yyyy-MM-dd"))
        print("Due:", dialog.due_date_edit.date().toString("yyyy-MM-dd"))
        print("Status:", dialog.status_combo.currentText())