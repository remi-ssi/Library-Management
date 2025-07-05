import os
import re
import sys
import shutil
import requests
import traceback
from dotenv import load_dotenv
from navbar_logic import nav_manager
from navigation_sidebar import NavigationSidebar
from PySide6.QtCore import Qt, QSize, QEvent, QPropertyAnimation, QTimer, QRect
from PySide6.QtGui import QFont, QIcon, QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QLineEdit, QScrollArea, QGridLayout,
    QTabWidget, QTextEdit, QMessageBox, QFormLayout, QDialog, QListWidget,
    QListWidgetItem, QGroupBox, QSpinBox, QFileDialog, QMenu, QComboBox,
    QToolTip)

from tryDatabase import DatabaseSeeder
load_dotenv()

# Utility functions for book management
def validate_isbn(isbn):
    if not isbn:
        return False
        
    # Clean ISBN by removing non-alphanumeric characters except X
    isbn_clean = re.sub(r'[^0-9X]', '', isbn.upper())
    
    if len(isbn_clean) not in [10, 13]:
        return False
        
    if len(isbn_clean) == 10:
        return _validate_isbn10(isbn_clean)
    return _validate_isbn13(isbn_clean)

# for ISBN-10 validation
def _validate_isbn10(isbn):
    if len(isbn) != 10:
        return False
    total = 0 
    for i in range(9):
        if not isbn[i].isdigit():
            return False
        total += int(isbn[i]) * (10 - i) 
    if isbn[9] == 'X':
        total += 10
    elif isbn[9].isdigit():
        total += int(isbn[9])
    else:
        return False
    return total % 11 == 0

# for ISBN-13 validation
def _validate_isbn13(isbn):
    if len(isbn) != 13:
        return False
    if not isbn.isdigit():
        return False 
    total = 0 
    for i in range(12):
        if i % 2 == 0:
            total += int(isbn[i])
        else:
            total += int(isbn[i]) * 3
    check_digit = (10 - (total % 10)) % 10
    return check_digit == int(isbn[12])

# Utility functions for book data processing
def clean_isbn(isbn):
    #Clean and format ISBN by removing non-alphanumeric characters
    return re.sub(r'[^0-9X]', '', isbn.strip().upper())

# Validate shelf format (A-Z followed by 1-5 digits)
def validate_shelf_format(shelf):
    return bool(re.match(r'^[A-Z][0-9]{1,5}$', shelf))

# to format author list for display
def format_authors_display(authors):
    if isinstance(authors, list):
        author_text = ', '.join(authors[:2])
        if len(authors) > 2:
            author_text += f" +{len(authors)-2} more"
        return author_text
    return str(authors)

def format_authors_for_processing(author_text):
    return list(set([a.strip() for a in author_text.strip().split(',') if a.strip()]))

# to load and scale pixmap safely
def load_pixmap_safely(image_path, target_size):
    try:
        if image_path and isinstance(image_path, str) and os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                return pixmap.scaled(target_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
    return None

# Dialog for previewing book details before editing
class BookPreviewDialog(QDialog):
    def __init__(self, book_data, parent=None):
        #Initialize preview dialog with book data
        super().__init__(parent)
        self.book_data = book_data
        self.parent_window = parent
        self.setWindowTitle(f"Book Preview - {book_data['title']}")
        self.setFixedSize(900, 750)
        self.setStyleSheet("""QDialog {background-color: #f1efe3;} """)
        self.init_ui()
      
    def init_ui(self):
        #Create and setup the user interface
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header section with book title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(30, 5, 10, 5)
        
        title = QLabel(self.book_data['title'])
        title.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 28px;
                font-weight: bold;
                padding: 10px 15px;
                margin: 5px;
            }
        """)
        title.setWordWrap(True)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Main content area with cover and details
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 16px;
                border: 2px solid #dbcfc1;
            }
        """)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(30)
        
        # Left side - Book cover image display
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)
        
        # Book cover image
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(200, 280)
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 2px solid #dbcfc1;
                border-radius: 12px;
                color: #999999;
            }
        """)
        
        # Load book cover using utility function
        image_path = self.book_data.get("image", "")
        scaled_pixmap = load_pixmap_safely(image_path, QSize(200, 280))
        
        if scaled_pixmap:
            self.cover_label.setPixmap(scaled_pixmap)
            self.cover_label.setStyleSheet("""
                QLabel {
                    border: 2px solid #dbcfc1;
                    border-radius: 12px;
                }
            """)
        else:
            self.cover_label.setText("No Cover Available")
        
        left_layout.addWidget(self.cover_label, 0, Qt.AlignCenter)
        left_layout.addStretch()
        
        # Right side - Book details information
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)
        
        # Shared style for info labels
        info_style = """
            QLabel {
                color: #5C4033;
                font-size: 16px;
                padding: 12px 15px;
                background-color: #f9f9f9;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
                margin: 2px;
            }
        """
        
        # Author information - handle list format
        authors = self.book_data.get('author', [])
        author_text = format_authors_display(authors)
        
        author_label = QLabel(f"<b>Author:</b> {author_text}")
        author_label.setStyleSheet(info_style)
        author_label.setWordWrap(True)
        right_layout.addWidget(author_label)
        
        # Genre information - handle list format
        genres = self.book_data.get('genre', [])
        if isinstance(genres, list):
            genre_text = ', '.join(genres)
        else:
            genre_text = str(genres)
        
        genre_label = QLabel(f"<b>Genre:</b> {genre_text}")
        genre_label.setStyleSheet(info_style)
        genre_label.setWordWrap(True)
        right_layout.addWidget(genre_label)
        
        # ISBN information
        isbn = self.book_data.get('isbn', 'N/A')
        isbn_label = QLabel(f"<b>ISBN:</b> {isbn}")
        isbn_label.setStyleSheet(info_style)
        right_layout.addWidget(isbn_label)
        
        # Shelf location - ensure we display ShelfName, not ShelfId
        shelf = self.book_data.get('shelf', 'N/A')
        
        # If shelf is a numeric ID, convert it to shelf name
        if shelf and str(shelf).isdigit():
            try:
                # Get shelf name from database using the ShelfId
                db_seeder = DatabaseSeeder()
                shelf_records = db_seeder.get_all_records("BookShelf", getattr(self.parent_window, 'librarian_id', 1))
                shelf_name = next(
                    (record['ShelfName'] for record in shelf_records 
                     if record.get('ShelfId') == int(shelf)), 
                    f"Shelf {shelf}"  # Fallback to "Shelf {ID}" if not found
                )
                shelf = shelf_name
            except Exception as e:
                print(f"Error converting ShelfId to ShelfName: {e}")
                shelf = f"Shelf {shelf}"  # Fallback display
        
        shelf_label = QLabel(f"<b>Shelf:</b> {shelf}")
        shelf_label.setStyleSheet(info_style)
        right_layout.addWidget(shelf_label)
        
        # Copies information
        total_copies = self.book_data.get('copies', 0)
        available_copies = self.book_data.get('available_copies', 0)
        copies_label = QLabel(f"<b>Copies:</b> {available_copies} available of {total_copies} total")
        copies_label.setStyleSheet(info_style)
        right_layout.addWidget(copies_label)
        
        # Description section
        description = self.book_data.get('description', 'No description available')
        desc_label = QLabel("<b>Description:</b>")
        desc_label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 5px;
                margin-top: 5px;
            }
        """)
        right_layout.addWidget(desc_label)
        
        desc_text = QTextEdit()
        desc_text.setPlainText(description)
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(120)
        desc_text.setStyleSheet("""
            QTextEdit {
                color: #5C4033;
                font-size: 14px;
                padding: 15px;
                background-color: #f9f9f9;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        right_layout.addWidget(desc_text)
        
        right_layout.addStretch()
        
        content_layout.addWidget(left_widget)
        content_layout.addWidget(right_widget, 1)
        
        layout.addWidget(content_widget)
        
        # Action buttons section
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Edit button
        edit_btn = QPushButton("Edit Book")
        edit_btn.setFixedSize(120, 45)
        edit_btn.clicked.connect(self.open_edit_view)
        edit_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background-color: #5C4033;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedSize(120, 45)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 2px solid #5C4033;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        button_layout.addStretch()
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(close_btn)        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
    
    def open_edit_view(self):
        #Open edit view for this book"""
        self.accept()  # Close the preview dialog
        if self.parent_window:
            self.parent_window.show_book_edit_view(self.book_data)
        else:
            print("[ERROR] parent_window is None!")

class BookEditView(QWidget):
    """Widget for editing existing book details with validation and database updates"""
    
    def __init__(self, book_data, parent_window):
        super().__init__()
        
        # Initialize core properties
        self.book_data = book_data 
        self.parent_window = parent_window
        
        # Validate parent window connection
        if not parent_window:
            return
        
        # Initialize database connection
        from tryDatabase import DatabaseSeeder
        self.db_seeder = DatabaseSeeder()
        
        # Configure widget properties and initialize UI
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface for book editing"""
        # Main layout setup with proper spacing and margins
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Create header section, form, and buttons
        layout.addLayout(self._create_header())
        layout.addWidget(self._create_title_label())
        layout.addWidget(self._create_form_widget())
        layout.addLayout(self._create_button_layout())
        layout.addStretch()

    def _create_header(self):
        """Create header section with back button"""
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Back to Books")
        back_btn.setFixedSize(150, 40)
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet("""
            QPushButton {
                color: #5C4033; font-size: 16px; font-weight: bold; background-color: #f0f0f0;
                border: 2px solid #5C4033; border-radius: 10px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
        """)
        
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        return header_layout

    def _create_title_label(self):
        """Create page title label"""
        title = QLabel(f"Edit Book: {self.book_data['title']}")
        title.setStyleSheet("""
            QLabel { color: #5C4033; font-size: 30px; font-weight: bold; padding: 10px 0px; }
        """)
        return title

    def _create_form_widget(self):
        """Create form container with all input fields"""
        form_widget = QWidget()
        form_widget.setStyleSheet("""
            QWidget { background-color: white; border-radius: 16px; border: 2px solid #dbcfc1; }
        """)
        
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        # Create all input fields
        self._create_form_fields()
        
        # Add fields to form layout
        fields = [
            ("Title:", self.title_input),
            ("Author:", self.author_input),
            ("Genre:", self.genre_input),
            ("ISBN:", self.isbn_input),
            ("Total copy of books:", self.copies_input),
            ("Shelf No.:", self.shelf_input),
            ("Description:", self.description_input)
        ]
        
        for label_text, field in fields:
            form_layout.addRow(self._create_label(label_text), field)
        
        return form_widget

    def _create_form_fields(self):
        """Create and configure all form input fields"""
        # Read-only fields
        self.title_input = self._create_readonly_field(self.book_data.get('title', ''))
        self.author_input = self._create_readonly_field(self._format_list_field(self.book_data.get('author', '')))
        self.genre_input = self._create_readonly_field(self._format_list_field(self.book_data.get('genre', '')))
        self.isbn_input = self._create_readonly_field(str(self.book_data.get('isbn', '')))
        
        # Editable fields
        self.copies_input = self._create_editable_field(str(self.book_data.get('copies', 1)))
        self.shelf_input = self._create_shelf_dropdown()
        self.description_input = self._create_description_field()

    def _format_list_field(self, field_value):
        """Format list fields (author/genre) for display"""
        if isinstance(field_value, list):
            return ', '.join(field_value)
        return str(field_value)

    def _create_readonly_field(self, value):
        """Create a read-only input field"""
        field = QLineEdit(value)
        field.setReadOnly(True)
        field.setStyleSheet("""
            QLineEdit {
                color: #666666; font-size: 16px; padding: 10px; background-color: #f5f5f5;
                border: 2px solid #dbcfc1; border-radius: 10px;
            }
        """)
        return field

    def _create_editable_field(self, value):
        """Create an editable input field"""
        field = QLineEdit(value)
        field.setStyleSheet("""
            QLineEdit {
                color: #5C4033; font-size: 16px; padding: 10px; background-color: white;
                border: 2px solid #dbcfc1; border-radius: 10px;
            }
            QLineEdit:focus { border-color: #5C4033; }
        """)
        return field

    def _create_shelf_dropdown(self):
        """Create and populate shelf dropdown"""
        dropdown = QComboBox()
        dropdown.setEditable(False)
        dropdown.setStyleSheet("""
            QComboBox {
                color: #5C4033; font-size: 16px; padding: 10px; background-color: white;
                border: 2px solid #dbcfc1; border-radius: 10px;
            }
            QComboBox:focus { border-color: #5C4033; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow {
                image: none; border: 1px solid #5C4033; width: 10px; height: 10px; background-color: #5C4033;
            }
        """)
        
        self._populate_shelf_dropdown(dropdown)
        return dropdown

    def _create_description_field(self):
        """Create description text area"""
        field = QTextEdit(self.book_data.get('description', 'No description available'))
        field.setMaximumHeight(150)
        field.setStyleSheet("""
            QTextEdit {
                color: #5C4033; font-size: 15px; padding: 10px; background-color: white;
                border: 2px solid #dbcfc1; border-radius: 16px;
            }
            QTextEdit:focus { border-color: #5C4033; }
        """)
        return field

    def _create_button_layout(self):
        """Create action buttons layout"""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Button configurations: (text, callback, style_class)
        buttons_config = [
            ("Save Changes", self.save_changes, "save"),
            ("Delete Book", self.delete_book, "delete"),
            ("Cancel", self.go_back, "cancel")
        ]
        
        for text, callback, style_class in buttons_config:
            button = QPushButton(text)
            button.setFixedSize(150, 50)
            button.clicked.connect(callback)
            button.setStyleSheet(self._get_button_style(style_class))
            button_layout.addWidget(button)
        
        return button_layout

    def _get_button_style(self, style_class):
        """Get button styling based on class"""
        styles = {
            "save": """
                QPushButton {
                    color: white; font-size: 16px; font-weight: bold; background-color: #5C4033;
                    border: none; border-radius: 16px;
                }
                QPushButton:hover { background-color: #8B4513; }
            """,
            "delete": """
                QPushButton {
                    color: white; font-size: 16px; font-weight: bold; background-color: #CC4125;
                    border: none; border-radius: 16px;
                }
                QPushButton:hover { background-color: #E55B4A; }
            """,
            "cancel": """
                QPushButton {
                    color: #5C4033; font-size: 16px; font-weight: bold; background-color: #f0f0f0;
                    border: 2px solid #5C4033; border-radius: 10px;
                }
                QPushButton:hover { background-color: #e0e0e0; }
            """
        }
        return styles.get(style_class, "")

    def _create_label(self, text):
        """Create a styled label for form fields"""
        label = QLabel(text)
        label.setStyleSheet("QLabel { color: #5C4033; font-size: 16px; font-weight: bold; }")
        return label
    
    def _populate_shelf_dropdown(self, dropdown):
        """Populate shelf dropdown with available shelves from database"""
        try:  
            # Get librarian_id and shelf records
            librarian_id = getattr(self.parent_window, 'librarian_id', 1)
            shelf_records = self.db_seeder.get_all_records("BookShelf", librarian_id)
            
            # Extract shelf names, filtering out empty values
            available_shelves = [record['ShelfName'] for record in shelf_records if record.get('ShelfName')] 
            
            # Create default shelf if none exist
            if not available_shelves:
                available_shelves = self._create_default_shelf(librarian_id)
            
            # Populate dropdown with shelves
            dropdown.addItems(available_shelves)
            
            # Set current shelf selection
            self._set_current_shelf_selection(dropdown, available_shelves)
                    
        except Exception:
            # Fallback to default shelf on error
            dropdown.addItem("A1")
            dropdown.setCurrentIndex(0)

    def _create_default_shelf(self, librarian_id):
        """Create default shelf A1 if no shelves exist"""
        try:
            self.db_seeder.seed_data("BookShelf", [{"ShelfName": "A1", "LibrarianID": librarian_id}], 
                                     ["ShelfName", "LibrarianID"])
            return ["A1"]
        except Exception:
            return ["A1"]

    def _set_current_shelf_selection(self, dropdown, available_shelves):
        """Set current shelf selection in dropdown"""
        current_shelf = self.book_data.get('shelf', '')
        
        if current_shelf:
            index = dropdown.findText(current_shelf)
            if index >= 0:
                dropdown.setCurrentIndex(index)
            else:
                # Add current shelf if not in list
                dropdown.addItem(current_shelf)
                index = dropdown.findText(current_shelf)
                if index >= 0:
                    dropdown.setCurrentIndex(index)
        elif available_shelves:
            dropdown.setCurrentIndex(0)
    
    def _get_or_create_shelf_id(self, shelf_name):
        """Get shelf ID from database or create new shelf if it doesn't exist"""
        try:
            # Get librarian_id and shelf records
            librarian_id = getattr(self.parent_window, 'librarian_id', 1)
            shelf_records = self.db_seeder.get_all_records("BookShelf", librarian_id)
            
            # Find existing shelf by name
            for shelf_record in shelf_records:
                if shelf_record['ShelfName'] == shelf_name:
                    return shelf_record['ShelfId']
            
            # Create new shelf if not found
            self.db_seeder.seed_data("BookShelf", [{"ShelfName": shelf_name, "LibrarianID": librarian_id}], 
                                     ["ShelfName", "LibrarianID"])
            
            # Get the newly created shelf ID
            shelf_records = self.db_seeder.get_all_records("BookShelf", librarian_id)
            for shelf_record in shelf_records:
                if shelf_record['ShelfName'] == shelf_name:
                    return shelf_record['ShelfId']
            
        except Exception:
            # Fallback: use the shelf name
            return shelf_name
        
        return shelf_name
    
    def save_changes(self):
        """Save changes to book details after validation"""
        # Validate input fields
        if not self._validate_input():
            return
        
        try:
            # Calculate copy availability and prepare updates
            update_data = self._prepare_update_data()
            
            # Update database
            if self._update_database(update_data):
                # Show success and refresh parent window
                self._show_success_message(update_data)
                self._refresh_parent_window()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error updating book: {str(e)}")

    def _validate_input(self):
        """Validate user input fields"""
        # Validate copies input
        copies_text = self.copies_input.text().strip()
        if not copies_text.isdigit() or int(copies_text) < 0:
            QMessageBox.warning(self, "Validation Error", "Total copies must be a non-negative integer")
            return False
        
        # Validate shelf format using utility function
        shelf = self.shelf_input.currentText().strip()
        if not validate_shelf_format(shelf):
            QMessageBox.warning(self, "Validation Error", 
                               "Shelf number must be one letter (A-Z) followed by 1 to 5 digits. (e.g. A1, B12, C345)")
            return False
        
        return True

    def _prepare_update_data(self):
        """Prepare data for database update"""
        # Get input values
        copies_text = self.copies_input.text().strip()
        shelf = self.shelf_input.currentText().strip()
        description = self.description_input.toPlainText().strip()
        
        # Calculate copy availability
        old_total_copies = self.book_data.get('copies', 0)  
        old_available = self.book_data.get('available_copies', 0)
        new_total_copies = int(copies_text)
        
        # Calculate borrowed copies and new availability
        borrowed_copies = old_total_copies - old_available
        new_available_copies = max(0, new_total_copies - borrowed_copies)
        
        # Get or create shelf ID for database storage
        shelf_id = self._get_or_create_shelf_id(shelf)
        
        # Update book data in memory
        self.book_data.update({
            'copies': new_total_copies,
            'available_copies': new_available_copies,
            'shelf': shelf,
            'description': description
        })
        
        return {
            'shelf': shelf,
            'shelf_id': shelf_id,
            'description': description,
            'total_copies': new_total_copies,
            'available_copies': new_available_copies
        }

    def _update_database(self, update_data):
        """Update book data in database"""
        # Get book code for database update
        book_code = self.book_data.get('book_code')
        if not book_code:
            QMessageBox.warning(self, "Error", "Cannot update: Book code not found")
            return False
        
        # Prepare database updates
        book_updates = {
            'BookDescription': update_data['description'],
            'BookShelf': update_data['shelf_id'],
            'BookTotalCopies': update_data['total_copies'],
            'BookAvailableCopies': update_data['available_copies']
        }
        
        # Execute database update
        try:
            update_success = self.db_seeder.update_table("Book", book_updates, "BookCode", book_code)
            
            if update_success is False:
                QMessageBox.warning(self, "Error", "Failed to update book in database. Please try again.")
                return False
            
            return True
            
        except Exception as update_error:
            QMessageBox.warning(self, "Error", f"Database update failed: {str(update_error)}")
            return False

    def _show_success_message(self, update_data):
        """Show success message to user after successful update"""
        description = update_data['description']
        description_preview = description[:50] + ('...' if len(description) > 50 else '')
        
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setText(f"Book '{self.book_data['title']}' has been updated successfully!\n\n"
                   f"Updated fields:\n"
                   f"• Description: {description_preview}\n"
                   f"• Shelf: {update_data['shelf']}\n"
                   f"• Total Copies: {update_data['total_copies']}")
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def _refresh_parent_window(self):
        """Refresh parent window display with updated book data"""
        # Reload books data from database and switch to books view
        if hasattr(self.parent_window, 'load_books_from_database'):
            self.parent_window.load_books_from_database()
            
        if hasattr(self.parent_window, 'show_books_view'):
            self.parent_window.show_books_view()
    def delete_book(self):
        """Delete book after confirmation"""
        # Confirm deletion with user
        reply = QMessageBox.question(
            self, 'Confirm Deletion', 
            f"Are you sure you want to delete '{self.book_data['title']}'?\n\n"
            f"This will permanently remove the book and all related author and genre information.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Get book code for deletion
                book_code = self.book_data.get('book_code')
                if not book_code:
                    QMessageBox.warning(self, "Error", "Cannot delete: Book code not found")
                    return
                
                # Delete from database
                self.db_seeder.delete_table("Book", "BookCode", book_code)
                
                # Show success message
                QMessageBox.information(self, "Deleted", 
                                      f"Book '{self.book_data['title']}' has been deleted successfully!")
                
                # Refresh parent window and return to books view
                self.parent_window.load_books_from_database()
                self.parent_window.show_books_view()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error deleting book: {e}")
    
    def go_back(self):
        """Return to books view without saving changes"""
        self.parent_window.show_books_view()

class AddBookDialog(QDialog):
    """Dialog for adding new books with API verification and manual entry options"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize parent reference and database connection
        self.parent = parent
        self.db_seeder = DatabaseSeeder()
        
        # Get librarian_id from parent for database operations
        self.librarian_id = getattr(parent, 'librarian_id', None) if parent else None
        
        # Track API-found book data vs manual entry
        self.found_book_data = None
        
        # Configure dialog window properties
        self.setWindowTitle("Add New Book")
        self.setFixedSize(500, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
            }
        """)
        
        # Initialize user interface components
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface with input fields, results display, and buttons"""
        # Create main vertical layout with proper spacing
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Create and add book information input section
        layout.addWidget(self.create_input_section())
        
        # Create and add book results display section
        layout.addWidget(self.create_results_section())
        
        # Create and add action buttons section
        layout.addWidget(self.create_buttons_section())
    
    def create_input_section(self):
        """Create the book information input section with title, author, and ISBN fields"""
        # Book Information Input Section container
        info_group = QWidget()
        info_group.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #dbcfc1;
            }
            QLabel {
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(20, 20, 20, 20)
        info_layout.setSpacing(30)

        # Section title
        section_title = QLabel("Book Information")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                padding-top: 5px;
                padding-bottom: 12px;
            }
        """)
        info_layout.addWidget(section_title)

        # Create form layout for input fields
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # Create styled input fields
        input_style = """
            QLineEdit {
                color: #5C4033;
                font-size: 16px;
                padding: 12px 20px;
                background-color: white;
                border: 2px solid #dbcfc1;
                border-radius: 22px;
            }
            QLineEdit:focus {
                border-color: #5C4033;
            }
            QLineEdit::placeholder {
                color: #999999;
            }
        """

        # Title input field
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter Title")
        self.title_input.setStyleSheet(input_style)

        # Author input field
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Enter Author")
        self.author_input.setStyleSheet(input_style)

        # ISBN input field
        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText("Enter ISBN")
        self.isbn_input.setStyleSheet(input_style)

        # Add input fields to form layout
        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Author:", self.author_input)
        form_layout.addRow("ISBN:", self.isbn_input)
        
        info_layout.addLayout(form_layout)

        # Search button to verify book information via API
        search_btn = QPushButton("Search & Verify Book")
        search_btn.clicked.connect(self.search_book)
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C4033;
                color: white;
                padding: 14px;
                border: none;
                border-radius: 22px;
                font-size: 16px;;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        info_layout.addWidget(search_btn)
        
        return info_group
    
    def create_results_section(self):
        """Create the book results display section with cover preview and book information"""
        # Book Results Display Section container
        results_group = QWidget()
        results_group.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #dbcfc1;
            }
            QLabel {
                color: #5C4033;
                font-size: 16px;
                background: transparent;
            }
        """)
        results_layout = QHBoxLayout(results_group)
        results_layout.setContentsMargins(20, 20, 20, 20)
        results_layout.setSpacing(20)

        # Create left section with book cover preview
        left_section = self.create_cover_preview_section()
        
        # Create right section with book information display
        right_section = self.create_info_display_section()

        # Add both sections to results layout
        results_layout.addWidget(left_section)
        results_layout.addWidget(right_section)

        return results_group
    
    def create_cover_preview_section(self):
        """Create the book cover preview section"""
        left_section = QWidget()
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)

        # Book cover preview label
        self.book_preview = QLabel()
        self.book_preview.setFixedSize(180, 210)
        self.book_preview.setAlignment(Qt.AlignCenter)
        self.book_preview.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #dbcfc1;
                border-radius: 15px;
                color: #999999;
            }
        """)
        self.book_preview.setText("Book Cover Preview")
        left_layout.addWidget(self.book_preview, 0, Qt.AlignCenter)

        return left_section
    
    def create_info_display_section(self):
        """Create the book information display section with all info labels"""
        right_section = QWidget()
        right_layout = QVBoxLayout(right_section)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(10)

        # Initialize info display labels
        self.info_title = QLabel("Title: ")
        self.info_author = QLabel("Author: ")
        self.info_publisher = QLabel("Publisher: ")
        self.info_isbn = QLabel("ISBN: ")
        self.info_genre = QLabel("Genre: ")
        self.info_published = QLabel("Published: ")

        # Apply consistent styling to all info labels
        info_style = """
            QLabel {
                color: #5C4033;
                font-size: 14px;
                padding: 5px;
                background-color: #f9f9f9;
                border-radius: 15px;
            }
        """
        info_labels = [self.info_title, self.info_author, self.info_publisher,
                      self.info_isbn, self.info_genre, self.info_published]
        
        for label in info_labels:
            label.setStyleSheet(info_style)
            label.setWordWrap(True)
            right_layout.addWidget(label)
        
        right_layout.addStretch()
        return right_section
    
    def create_buttons_section(self):
        """Create the action buttons section with Add Book and Cancel buttons"""
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        
        # Add Book button
        add_btn = QPushButton("Add Book")
        add_btn.clicked.connect(self.add_book)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C4033;
                color: white;
                padding: 15px;
                border: none;
                border-radius: 22px;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #5C4033;
                padding: 12px;
                border: 2px solid #5C4033;
                border-radius: 22px;
                font-size: 16px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        
        # Add buttons to layout
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        
        return button_container
    
    
    def reset_cover_preview(self):
        """Reset the book cover preview and information labels to default state"""
        # Clear the cover image and reset to placeholder
        self.book_preview.setPixmap(QPixmap())
        self.book_preview.setText("Book Cover Preview")   
        self.book_preview.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #dbcfc1;
                border-radius: 15px;
                color: #999999;
            }
        """)
        
        # Reset all information display labels to default values
        default_labels = {
            self.info_title: "Title: ",
            self.info_author: "Author: ",
            self.info_publisher: "Publisher: ",
            self.info_isbn: "ISBN: ",
            self.info_genre: "Genre: ",
            self.info_published: "Published: "
        }
        
        for label, text in default_labels.items():
            label.setText(text)
       
    def search_book(self):
        """Search for book information using Google Books API"""
        # Get user input and clean ISBN using shared utility
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = clean_isbn(self.isbn_input.text().strip())

        # Validate that all required fields are filled
        if not title or not author or not isbn:
            QMessageBox.information(self, "Search Error", "Please fill all required fields: Title, Author, and ISBN")
            return

        # Validate ISBN using shared utility function
        if isbn and not validate_isbn(isbn):
            QMessageBox.warning(self, "Invalid ISBN", "The provided ISBN is invalid. Please correct the ISBN")
            self.found_book_data = None
            self.reset_cover_preview() 
            return
            
        try:
            # Clear previous preview before searching
            self.reset_cover_preview()
            
            # Search using Google Books API
            self.search_via_api(title, author, isbn)
                
        except requests.exceptions.RequestException as e:
            # Handle network connectivity errors
            QMessageBox.warning(self, "Network Error", "Unable to search books. Please check your internet connection")
            self.found_book_data = None
            self.reset_cover_preview()
            
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors (API key issues, etc.)
            if hasattr(self, 'response') and self.response.status_code == 403:
                QMessageBox.warning(self, "API Error", "Invalid API key")
            else:
                QMessageBox.warning(self, "API Error", f"HTTP Error: {e}")
            self.reset_cover_preview()
            
        except Exception as e:
            # Handle any other unexpected errors
            QMessageBox.warning(self, "Search Error", f"Error: {e}")
            self.open_manual_entry(title, author, isbn)
            self.reset_cover_preview()
    
    def search_via_api(self, title, author, isbn):
        """Perform the actual API search and process results"""
        # Prepare API request
        API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')
        
        # Build search query combining ISBN, title, and author
        search_term = [f"isbn:{isbn}", f"{title}", f"{author}"]
        query = " ".join(search_term) 
        url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}"
        
        # Send request to Google Books API
        self.response = requests.get(url, timeout=10)
        self.response.raise_for_status()
        data = self.response.json()

        # Check if API returned any results
        if 'items' not in data or len(data['items']) == 0:
            # No results found - redirect to manual entry
            self.open_manual_entry(title, author, isbn)
            return

        # Process the first result from API response
        self.process_api_result(data['items'][0]['volumeInfo'], isbn)
    
    def process_api_result(self, book_info, input_isbn):
        """Process API search result and update UI with book information"""
        # Extract ISBN data from API response (both ISBN-10 and ISBN-13)
        api_isbns = [
            clean_isbn(identifier['identifier'])
            for identifier in book_info.get('industryIdentifiers', [])
            if identifier['type'] in ['ISBN_10', 'ISBN_13']
        ]

        # Choose the best ISBN - prefer user input if valid, otherwise use first API ISBN
        found_isbn = input_isbn if (input_isbn and validate_isbn(input_isbn)) else api_isbns[0] if api_isbns else ''
        
        # Store book data from API response
        self.found_book_data = {
            'title': book_info.get('title', 'Unknown Title'),
            'author': format_authors_display(book_info.get('authors', ['Unknown Author'])),
            'isbn': found_isbn,
            'publisher': book_info.get('publisher', 'Unknown Publisher'),
            'description': book_info.get('description', ''),
            'categories': book_info.get('categories', ['']),
            'image_url': book_info.get('imageLinks', {}).get('thumbnail', '').replace('http:', 'https:'),
            'published_date': book_info.get('publishedDate', ''),
            'api_isbns': api_isbns
        }
        
        # Update UI with found book information
        self.update_book_info_display()
        
        # Load book cover image if available
        if 'imageLinks' in book_info:
            self.load_cover(self.found_book_data['image_url'])
    
    def update_book_info_display(self):
        """Update the UI labels with found book information"""
        if not self.found_book_data:
            return
            
        # Update all information display labels with found data
        info_updates = {
            self.info_title: f"Title: {self.found_book_data['title']}",
            self.info_author: f"Author: {self.found_book_data['author']}",
            self.info_publisher: f"Publisher: {self.found_book_data['publisher']}",
            self.info_isbn: f"ISBN: {self.found_book_data['isbn'] or 'N/A'}",
            self.info_genre: f"Genre: {format_authors_display(self.found_book_data['categories'])}",
            self.info_published: f"Published: {self.found_book_data['published_date']}"
        }
        
        for label, text in info_updates.items():
            label.setText(text)

    def open_manual_entry(self, title, author, isbn):
        """Open manual book entry dialog when API search fails or returns no results"""
        # Check for duplicate book in database before proceeding
        if not self.db_seeder.handleDuplication(tableName="Book", librarianID=self.librarian_id, column="ISBN", value=isbn):
            QMessageBox.information(self, "Duplicate Book", "This book already exists in the database.")
            return
        
        # Validate ISBN before opening manual entry dialog
        if isbn and not validate_isbn(isbn):
            QMessageBox.warning(self, "Invalid ISBN", "The provided ISBN is invalid. Please correct the ISBN")
            return
        
        # Prepare book data structure for manual entry
        book_data = {
            'title': title,
            'author': author if author else "Unknown Author",
            'isbn': isbn if isbn and validate_isbn(isbn) else '',
            'publisher': '',
            'description': '',
            'categories': [''],
            'image_url': '',
            'published_date': '',
            'image': ''
        }

        # Close current dialog and open details dialog for manual entry
        self.accept()
        self.open_book_details_dialog(book_data, is_found_book=False)
    
    def open_book_details_dialog(self, book_data, is_found_book):
        """Open BookDetailsDialog with proper configuration and styling"""
        # Create and configure BookDetailsDialog
        details_dialog = BookDetailsDialog(
            parent=self.parent,
            book_data=book_data,
            is_found_book=is_found_book
        )

        # Configure window properties for fullscreen display
        details_dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.Window)
        details_dialog.resize(QApplication.primaryScreen().availableSize() * 0.9)
        details_dialog.showFullScreen()  

        # Create and configure close button
        close_btn = self.create_close_button(details_dialog)

        # Apply fullscreen stylesheet to dialog
        self.apply_fullscreen_styles(details_dialog)
        
        # Execute dialog and handle result
        result = details_dialog.exec_()
        
        if result == QDialog.Accepted:
            # Book was successfully saved by BookDetailsDialog.save_book()
            # Refresh parent's books display if method exists
            if hasattr(self.parent, 'refresh_books_display'):
                self.parent.refresh_books_display()
            
            self.accept()
    
    def create_close_button(self, parent_dialog):
        """Create and configure the close button for dialogs"""
        close_btn = QPushButton("X", parent_dialog)
        close_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background-color: #5C4033;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 10px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        
        # Position and configure close button
        close_btn.setFixedSize(40, 40)
        dialog_width = parent_dialog.width()
        close_btn.move(dialog_width - 60, 20)
        close_btn.raise_()
        close_btn.clicked.connect(parent_dialog.reject)
        
        return close_btn
    
    def apply_fullscreen_styles(self, dialog):
        """Apply consistent fullscreen styling to dialogs"""
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
                font-size: 14px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background-color: #f0f0f0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #5C4033;
                border-radius: 6px;
                min-height: 30px;
            }
        """)
            
    def load_cover(self, image_url):
        """Download and display book cover image from URL"""
        try:
            # Download image from the provided URL
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Create QPixmap from downloaded image data
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            
            if not pixmap.isNull():
                # Scale and display the image
                self.display_cover_image(pixmap, response.content)
            else:
                # Image failed to load - show placeholder
                self.show_cover_placeholder()
                
        except Exception as e:
            # Handle any errors during image loading
            self.show_cover_error()
    
    def display_cover_image(self, pixmap, image_content):
        """Display the book cover image and save it locally"""
        # Scale image to fit preview area while maintaining aspect ratio
        scaled_pixmap = pixmap.scaled(
            self.book_preview.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Display the scaled image and clear placeholder styling
        self.book_preview.setPixmap(scaled_pixmap)
        self.book_preview.setStyleSheet("")

        # Save image locally in assets folder
        self.save_cover_locally(image_content)
    
    def save_cover_locally(self, image_content):
        """Save the book cover image to local assets folder"""
        # Create assets folder if it doesn't exist
        if not os.path.exists('assets'): 
            os.makedirs('assets')
            
        # Use ISBN for filename, fallback to 'temp' if not available
        isbn = self.found_book_data.get('isbn', 'temp')
        image_path = os.path.normpath(os.path.join('assets', f"book_cover_{isbn}.png"))
        
        # Write image data to local file
        with open(image_path, 'wb') as f:
            f.write(image_content)
            
        # Store local image path in book data
        self.found_book_data['image'] = image_path
    
    def show_cover_placeholder(self):
        """Show placeholder when cover image fails to load"""
        self.book_preview.setText("")
        self.book_preview.setStyleSheet("""
            QLabel {
                background-color: #dbcfc1;
                border-radius: 8px;
                border: 2px solid #5C4033;
            }
        """)
        if self.found_book_data:
            self.found_book_data['image'] = ''
    
    def show_cover_error(self):
        """Show error message when cover image cannot be loaded"""
        self.book_preview.setText("Cover not available")
        if self.found_book_data:
            self.found_book_data['image'] = ''
    
    def add_book(self):
        """Process the add book request and open BookDetailsDialog for final confirmation"""
        # Get and validate user input
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = clean_isbn(self.isbn_input.text().strip())

        # Ensure all required fields are provided
        if not title or not author or not isbn:
            QMessageBox.information(self, "Adding book Error", "Please fill in all required fields: Title, Author, and ISBN")
            return
            
        # Validate ISBN using shared utility function
        if isbn and not validate_isbn(isbn):
            QMessageBox.warning(self, "Validation Error", "Invalid ISBN")
            return

        # Prepare book data - use API data if available, otherwise use manual input
        book_data = self.found_book_data or {
            'title': title,
            'author': author if author else 'Unknown Author',
            'isbn': isbn if isbn and validate_isbn(isbn) else '',
            'publisher': '',
            'description': '',
            'categories': [''],
            'image_url': '',
            'published_date': '',
            'image': ''
        }
        
        # Close current dialog and open details dialog
        self.accept()
        self.open_book_details_dialog(book_data, is_found_book=bool(self.found_book_data))

class BookDetailsDialog(QDialog):
    """Dialog for entering and editing detailed book information with validation"""
    
    def __init__(self, parent=None, book_data=None, is_found_book=False):
        super().__init__(parent)
        
        # Initialize dialog properties and data
        self.parent = parent
        self.book_data = book_data or {}
        self.is_found_book = is_found_book
        self.image_preview_size = QSize(180, 210)
        self.selected_genres = []
        
        # Initialize database connection and librarian ID
        from tryDatabase import DatabaseSeeder
        self.db_seeder = DatabaseSeeder()
        self.librarian_id = getattr(parent, 'librarian_id', None) if parent else None
        
        # Set up UI and populate data
        self.setup_ui()
        self.populate_fields()

    def setup_ui(self):
        """Set up the user interface for the book details dialog"""
        # Configure dialog window properties
        self.setWindowTitle("Book Details")
        self.setStyleSheet('QDialog { background-color: #f1efe3; font-size: 14px; }')
        
        # Create main layout with scroll area for content
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 30)
        main_layout.setSpacing(20)

        # Add close button and scrollable content
        main_layout.addWidget(self._create_close_button_container())
        main_layout.addWidget(self._create_scroll_area())

    def _create_close_button_container(self):
        """Create container with close button positioned at top-right"""
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch()
        
        # Create and configure close button
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(40, 40)
        self.close_btn.setStyleSheet("""
            QPushButton {
                color: white; background-color: #CC4125; font-size: 18px; font-weight: bold;
                border: none; border-radius: 20px;
            }
            QPushButton:hover { background-color: #E55B4A; }
            QPushButton:pressed { background-color: #B71C1C; }
        """)
        self.close_btn.clicked.connect(self.reject)
        self.close_btn.setToolTip("Close")
        
        layout.addWidget(self.close_btn)
        return container

    def _create_scroll_area(self):
        """Create scrollable content area with all form sections"""
        # Create scroll area with content styling
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { width: 15px; background-color: #f0f0f0; border-radius: 6px; }
            QScrollBar::handle:vertical { background-color: #5C4033; border-radius: 6px; min-height: 30px; }
            QScrollBar::handle:vertical:hover { background-color: #8B4513; }
        """)
        
        # Create container widget for scrollable content
        content_widget = QWidget()
        content_widget.setMinimumWidth(800)
        content_widget.setStyleSheet("background-color: #f1efe3;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 0, 30, 30)
        content_layout.setSpacing(25)

        # Add dialog title
        title_label = QLabel("Enter Book Details")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 26px; font-weight: bold; color: #5C4033; margin-bottom: 10px; background: transparent;
            }
        """)
        content_layout.addWidget(title_label)

        # Add form sections
        content_layout.addWidget(self._create_book_info_section())
        content_layout.addWidget(self._create_library_and_cover_section())
        content_layout.addLayout(self._create_action_buttons())

        scroll_area.setWidget(content_widget)
        return scroll_area

    def _create_book_info_section(self):
        """Create the book information form section"""
        info_group = QGroupBox("Book Information")
        info_group.setStyleSheet("""
            QGroupBox {
                background-color: white; border-radius: 15px; border: 2px solid #dbcfc1;
                color: #5C4033; font-size: 25px; font-weight: bold; margin-top: 10px; padding-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left:8px; padding: 0 3px; }
        """)
        
        info_layout = QFormLayout(info_group)
        info_layout.setContentsMargins(15, 25, 15, 25)
        info_layout.setVerticalSpacing(20)
        info_layout.setHorizontalSpacing(15)
        
        # Get common styles
        input_style = self._get_input_field_style()
        label_style = self._get_form_label_style()
        
        # Create input fields
        self.title_edit = self._create_line_edit("Enter Title", input_style)
        self.author_edit = self._create_line_edit("Enter Author", input_style)
        self.isbn_edit = self._create_line_edit("Enter ISBN", input_style)
        self.publisher_edit = self._create_line_edit("Enter Publisher", input_style)
        
        # Create genre container and description text area
        self.genre_container = self._create_genre_selection_container(input_style)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter Description")
        self.description_edit.setStyleSheet(input_style)
        self.description_edit.setMinimumHeight(45)

        # Create form fields with labels
        form_fields = [
            ("Title:", self.title_edit), ("Author:", self.author_edit), ("ISBN:", self.isbn_edit),
            ("Publisher:", self.publisher_edit), ("Genre:", self.genre_container), ("Description:", self.description_edit)
        ]
        
        for label_text, field_widget in form_fields:
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            info_layout.addRow(label, field_widget)

        return info_group

    def _create_line_edit(self, placeholder, style):
        """Create a styled QLineEdit with placeholder text"""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setStyleSheet(style)
        line_edit.setFixedHeight(35)
        return line_edit

    def _create_genre_selection_container(self, input_style):
        """Create genre selection container with combo box and tags"""
        # Create main container for genre selection
        genre_container = QWidget()
        genre_layout = QVBoxLayout(genre_container)
        genre_layout.setContentsMargins(0, 0, 0, 0)
        genre_layout.setSpacing(10)

        # Add help text
        genre_help = QLabel("Select a genre or type a new one, then press Enter to add it")
        genre_help.setStyleSheet("QLabel { color: #777777; font-size: 12px; font-style: italic; background: transparent; border: none; }")
        genre_layout.addWidget(genre_help)

        # Create container for selected genre tags
        self.selected_genres_container = QWidget()
        self.selected_genres_layout = QHBoxLayout(self.selected_genres_container)
        self.selected_genres_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_genres_layout.setSpacing(5)
        self.selected_genres_layout.setAlignment(Qt.AlignLeft)

        # Create and configure genre combo box
        self.genre_combo = QComboBox()
        self.genre_combo.setStyleSheet(input_style)
        self.genre_combo.setFixedHeight(55)
        self.genre_combo.setEditable(True)
        self.genre_combo.setInsertPolicy(QComboBox.NoInsert)
        self.genre_combo.setPlaceholderText("Select or type a genre")

        # Add popular genres as options
        common_genres = [
            "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery", "Thriller", "Romance", 
            "Historical Fiction", "Biography", "Autobiography", "Self-Help", "Business", "Children's", 
            "Young Adult", "Poetry", "Science", "History", "Philosophy", "Religion", "Art", "Cooking"
        ]
        self.genre_combo.addItems(sorted(common_genres))

        # Connect genre selection signals
        self.genre_combo.currentIndexChanged.connect(self._add_current_genre_from_dropdown)
        self.genre_combo.lineEdit().returnPressed.connect(self._add_current_genre)

        # Add widgets to container
        genre_layout.addWidget(self.genre_combo)
        genre_layout.addWidget(self.selected_genres_container)
        return genre_container

    def _create_library_and_cover_section(self):
        """Create horizontal section with library info and book cover"""
        # Create horizontal container
        lib_cover_container = QWidget()
        lib_cover_layout = QHBoxLayout(lib_cover_container)
        lib_cover_layout.setContentsMargins(0, 0, 0, 0)
        lib_cover_layout.setSpacing(20)
        
        # Create library information section (60% width) and book cover section (40% width)
        lib_group = self._create_library_info_section()
        image_group = self._create_book_cover_section()
        
        # Add both sections with proportional widths
        lib_cover_layout.addWidget(lib_group, 6)
        lib_cover_layout.addWidget(image_group, 4)
        return lib_cover_container

    def _create_library_info_section(self):
        """Create library information form section"""
        lib_group = QGroupBox("Library Information")
        lib_group.setStyleSheet("""
            QGroupBox {
                background-color: white; border-radius: 15px; border: 2px solid #dbcfc1;
                color: #5C4033; font-size: 16px; font-weight: bold; margin-top: 10px; padding-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0px 5px; background: transparent; }
        """)
        
        lib_layout = QFormLayout(lib_group)
        lib_layout.setContentsMargins(15, 25, 15, 25)
        lib_layout.setVerticalSpacing(20)
        lib_layout.setHorizontalSpacing(15)

        # Create shelf dropdown and copies spin box
        self.shelf_edit = self._create_shelf_dropdown()
        
        self.copies_spin = QSpinBox()
        self.copies_spin.setMaximum(999)
        self.copies_spin.setMinimum(1)
        self.copies_spin.setValue(1)
        self.copies_spin.setStyleSheet(self._get_input_field_style())
        self.copies_spin.setFixedHeight(35)

        # Create labels and add to form
        label_style = self._get_form_label_style()
        shelf_label = QLabel("Shelf Number:")
        shelf_label.setStyleSheet(label_style)
        copies_label = QLabel("Total Copies:")
        copies_label.setStyleSheet(label_style)

        lib_layout.addRow(shelf_label, self.shelf_edit)
        lib_layout.addRow(copies_label, self.copies_spin)
        return lib_group

    def _create_shelf_dropdown(self):
        """Create and populate shelf dropdown with available shelves"""
        shelf_edit = QComboBox()
        shelf_edit.setEditable(False)
        shelf_edit.setPlaceholderText("Select Shelf")
        shelf_edit.setStyleSheet("""
            QComboBox {
                color: #5C4033; font-size: 14px; padding: 10px 20px; background-color: white;
                border: 1px solid #dbcfc1; border-radius: 5px;
            }
            QComboBox:focus { border: 1px solid #5C4033; }
            QComboBox::drop-down { border: none; width: 20px; }
            QComboBox::down-arrow { image: none; border: 1px solid #5C4033; width: 8px; height: 8px; background-color: #5C4033; }
            QComboBox[readOnly="true"] { background-color: #f5f5f5; color: #666666; }
        """)
        shelf_edit.setFixedHeight(35)

        # Populate shelf dropdown using database utility
        try:
            from tryDatabase import DatabaseSeeder
            db_seeder = DatabaseSeeder()
            librarian_id = getattr(self.parent, 'librarian_id', 1)
            shelf_records = db_seeder.get_all_records("BookShelf", librarian_id)
            available_shelves = [record['ShelfName'] for record in shelf_records if record.get('ShelfName')]
            
            # Create default shelf if none exist
            if not available_shelves:
                try:
                    db_seeder.seed_data("BookShelf", [{"ShelfName": "A1", "LibrarianID": librarian_id}], ["ShelfName", "LibrarianID"])
                    available_shelves = ["A1"]
                except Exception:
                    available_shelves = ["A1"]
            
            shelf_edit.addItems(available_shelves)
        except Exception:
            shelf_edit.addItem("A1")  # Fallback to default shelf

        return shelf_edit

    def _create_book_cover_section(self):
        """Create book cover upload and preview section"""
        image_group = QGroupBox("Book Cover")
        image_group.setStyleSheet("""
            QGroupBox {
                background-color: white; border-radius: 15px; border: 2px solid #dbcfc1;
                color: #5C4033; font-size: 16px; font-weight: bold; margin-top: 10px;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; background: transparent; }
        """)

        image_layout = QHBoxLayout(image_group)
        image_layout.setContentsMargins(15, 20, 15, 20)
        image_layout.setSpacing(15)

        # Create image preview container
        image_container = QWidget()
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(0, 0, 0, 0)
        image_container_layout.setSpacing(10)

        # Create image preview label
        self.image_preview = QLabel()
        self.image_preview.setFixedSize(self.image_preview_size)
        self.image_preview.setMinimumSize(80, 100)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("QLabel { background-color: #f5f5f5; border: 2px dashed #dbcfc1; border-radius: 10px; }")
        
        image_container_layout.addWidget(self.image_preview, alignment=Qt.AlignCenter)

        # Create image label and upload button
        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: none; background: transparent;")
        image_container_layout.addWidget(self.image_label)

        image_layout.addWidget(image_container)

        self.image_btn = QPushButton("Upload Cover")
        self.image_btn.clicked.connect(self._upload_image)
        self.image_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C4033; color: white; padding: 12px 20px; border: none;
                border-radius: 10px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background-color: #8B4513; }
        """)
        self.image_btn.setFixedHeight(45)
        image_layout.addWidget(self.image_btn, alignment=Qt.AlignCenter)

        # Load cover preview if book was found via API
        if self.is_found_book and self.book_data.get('image'):
            self._load_cover_preview()

        return image_group

    def _create_action_buttons(self):
        """Create save and cancel action buttons"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Create save and cancel buttons
        save_btn = QPushButton("Save Book")
        save_btn.clicked.connect(self._save_book)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C4033; color: white; padding: 14px 20px; border: none;
                border-radius: 10px; font-size: 16px; font-weight: bold; min-width: 150px;
            }
            QPushButton:hover { background-color: #8B4513; }
        """)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #CC4125; color: white; padding: 14px 20px; border: none;
                border-radius: 10px; font-size: 16px; font-weight: bold; min-width: 150px;
            }
            QPushButton:hover { background-color: #D2523C; }
        """)

        button_layout.addStretch(1)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        button_layout.addStretch()
        
        # Configure field editability based on whether book was found via API
        self._configure_field_editability()
        
        return button_layout

    def _configure_field_editability(self):
        """Configure field editability based on whether book was found via API"""
        if self.is_found_book:
            # Make certain fields read-only for API-found books
            readonly_fields = [self.title_edit, self.author_edit, self.isbn_edit, self.publisher_edit]
            for field in readonly_fields:
                field.setReadOnly(True)
            
            # Disable genre combo if valid categories exist
            if self.book_data.get('categories', ['N/A'])[0] != 'N/A':
                self.genre_combo.setEnabled(False)
        else:
            # Allow editing for manually entered books
            editable_fields = [self.title_edit, self.author_edit, self.isbn_edit, self.publisher_edit]
            for field in editable_fields:
                field.setReadOnly(False)
            self.genre_combo.setEnabled(True)

    def _get_input_field_style(self):
        """Get consistent styling for input fields"""
        return """
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: white; border: 1px solid #dbcfc1; border-radius: 5px;
                padding: 10px 20px; font-size: 14px; color: #5C4033;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus { border: 1px solid #5C4033; }
            QLineEdit[readOnly="true"], QTextEdit[readOnly="true"] { background-color: #f5f5f5; color: #666666; }
            QLineEdit::placeholder, QTextEdit::placeholder { color: #999999; }
            QSpinBox::up-button, QSpinBox::down-button { width: 16px; background-color: #f5f5f5; border: none; }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover { background-color: #e0e0e0; }
            QTextEdit { min-height: 30px; }
        """

    def _get_form_label_style(self):
        """Get consistent styling for form labels"""
        return """
            QLabel {
                color: #5C4033; font-size: 14px; font-weight: bold; background-color: #f9f9f9;
                border: 1px solid #dbcfc1; border-radius: 8px; padding: 8px 12px; margin-right: 10px;
            }
        """

    def _load_cover_preview(self):
        """Load book cover preview from local image file"""
        try:
            image_path = os.path.normpath(self.book_data['image'])
            pixmap = load_pixmap_safely(image_path, self.image_preview.size())
            
            if pixmap:
                self.image_preview.setPixmap(pixmap)
                self.image_preview.setScaledContents(True)
                self.image_label.setText(f"Image: {os.path.basename(image_path)}")
            else:
                self._show_image_error_state()
        except Exception:
            self._show_image_error_state()

    def _show_image_error_state(self):
        """Show error state when image cannot be loaded"""
        self.image_preview.setText("")
        self.image_preview.setStyleSheet("QLabel { background-color: #dbcfc1; border-radius: 8px; border: 2px solid #5C4033; }")
        self.image_label.setText("No image selected")

    def populate_fields(self):
        """Populate form fields with book data"""
        # Populate basic text fields
        self.title_edit.setText(self.book_data.get('title', ''))
        self.isbn_edit.setText(self.book_data.get('isbn', ''))
        self.publisher_edit.setText(self.book_data.get('publisher', ''))
        self.description_edit.setText(self.book_data.get('description', ''))
        
        # Handle author field using utility function
        author = self.book_data.get('author', '')
        self.author_edit.setText(format_authors_display(author))
        
        # Handle genres - ensure we have a list for processing
        genres = self.book_data.get('categories', [''])
        if not isinstance(genres, list):
            genres = [genres]
        
        self.selected_genres = [g.strip() for g in genres if g.strip()]
        self.update_genre_tags()
        
        # Set shelf value in combo box
        shelf = self.book_data.get('shelf', '')
        if shelf:
            index = self.shelf_edit.findText(shelf)
            if index >= 0:
                self.shelf_edit.setCurrentIndex(index)
            else:
                # Add shelf if not in list and select it
                self.shelf_edit.addItem(shelf)
                self.shelf_edit.setCurrentText(shelf)

    def _upload_image(self):
        """Handle book cover image upload"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Book Cover", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                # Create assets directory if it doesn't exist
                if not os.path.exists('assets'):
                    os.makedirs('assets')
                
                # Generate filename using ISBN or fallback to 'temp'
                isbn = clean_isbn(self.isbn_edit.text().strip()) or 'temp'
                filename = f"book_cover_{isbn}.png"
                image_path = os.path.normpath(os.path.join('assets', filename))
                
                # Copy file to assets directory
                shutil.copy(file_path, image_path)
                
                if os.path.exists(image_path):
                    # Update book data and UI with new image
                    self.book_data['image'] = image_path
                    self.image_label.setText(f"Image: {os.path.basename(image_path)}")
                    
                    # Load and display the image using utility function
                    pixmap = load_pixmap_safely(image_path, self.image_preview.size())
                    if pixmap:
                        self.image_preview.setPixmap(pixmap)
                        self.image_preview.setStyleSheet("")
                    else:
                        self._show_upload_error("Invalid image file")
                else:
                    self._show_upload_error("Image copy failed")
                    
            except Exception:
                self._show_upload_error("Image upload failed")

    def _show_upload_error(self, error_text):
        """Show error state for image upload"""
        self._show_image_error_state()
        self.image_label.setText(error_text)
 
    def _save_book(self):
        """Save book information to the database with validation"""
        # Validate all required fields
        if not self._validate_required_fields():
            return
            
        # Clean and validate ISBN using utility functions
        isbn = clean_isbn(self.isbn_edit.text().strip())
        if isbn and not validate_isbn(isbn):
            QMessageBox.warning(self, "Validation Error", "Invalid ISBN")
            return
        
        # Check for duplicate book in database
        if not self.db_seeder.handleDuplication(tableName="Book", librarianID=self.librarian_id, column="ISBN", value=isbn):
            QMessageBox.information(self, "Duplicate Book", "This book already exists in the database.")
            return
        
        # Validate shelf format using utility function
        shelf = self.shelf_edit.currentText().strip()
        if not validate_shelf_format(shelf):
            QMessageBox.warning(self, "Validation Error", "Shelf number must be one letter (A-Z) followed by 1 to 5 digits. (e.g. A1, B12, C345)")
            return
            
        # Process authors and genres using utility functions
        authors = format_authors_for_processing(self.author_edit.text().strip())
        genres = list(set(self.selected_genres))
        
        if not genres:
            QMessageBox.warning(self, "Validation Error", "At least one(1) genre is required")
            return

        try:
            # Prepare book data for saving
            self._prepare_book_data_for_save(isbn, authors, genres, shelf)
            
            # Save to database
            book_code = self._save_to_database()
            
            # Save related data (authors and genres)
            self._save_related_data(book_code, authors, genres)
            
            # Show success and close
            self._handle_save_success()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error saving book to database: {e}")

    def _validate_required_fields(self):
        """Validate all required form fields"""
        required_fields = [
            (self.title_edit.text().strip(), "Title is required"),
            (self.author_edit.text().strip(), "Author is required"),
            (self.isbn_edit.text().strip(), "ISBN is required"),
            (self.publisher_edit.text().strip(), "Publisher is required"),
            (self.description_edit.toPlainText().strip(), "Description is required"),
            (self.shelf_edit.currentText().strip(), "Shelf number is required")
        ]
        
        for value, error_msg in required_fields:
            if not value:
                QMessageBox.warning(self, "Validation Error", error_msg)
                return False
        return True

    def _prepare_book_data_for_save(self, isbn, authors, genres, shelf):
        """Prepare book data dictionary for database save"""
        self.book_data = {
            'title': self.title_edit.text().strip(),
            'author': authors,
            'isbn': isbn,
            'publisher': self.publisher_edit.text().strip(),
            'genre': genres,
            'description': self.description_edit.toPlainText().strip(),
            'shelf': shelf,
            'copies': self.copies_spin.value(),
            'image': self.book_data.get('image', ''),
            'available_copies': self.copies_spin.value(),
            'image_url': self.book_data.get('image_url', '')
        }

    def _save_to_database(self):
        """Save main book record to database and return book code"""
        # Find or create shelf ID
        shelf_id = self._get_or_create_shelf_id(self.book_data['shelf'])
        
        # Prepare book data for database insertion
        book_data = {
            'BookTitle': self.book_data['title'],
            'Publisher': self.book_data['publisher'],
            'BookDescription': self.book_data['description'],
            'BookShelf': shelf_id,
            'ISBN': self.book_data['isbn'],
            'BookTotalCopies': self.book_data['copies'],
            'BookAvailableCopies': self.book_data['available_copies'],
            'BookCover': self.book_data['image'],
            'LibrarianID': self.librarian_id
        }

        # Insert main book record
        book_columns = ['BookTitle', 'Publisher', 'BookDescription', 'BookShelf', 'ISBN', 
                       'BookTotalCopies', 'BookAvailableCopies', 'BookCover', 'LibrarianID']
        
        self.db_seeder.seed_data(tableName="Book", data=[book_data], columnOrder=book_columns)

        # Retrieve the BookCode of the newly inserted book
        return self._get_inserted_book_code()

    def _get_or_create_shelf_id(self, shelf_name):
        """Get shelf ID from database or create new shelf if it doesn't exist"""
        shelf_id = None
        
        # Search for existing shelf
        shelf_records = self.db_seeder.get_all_records("BookShelf", self.librarian_id)
        for shelf_record in shelf_records:
            if shelf_record['ShelfName'] == shelf_name:
                shelf_id = shelf_record['ShelfId']
                break
        
        # Create new shelf if it doesn't exist
        if shelf_id is None:
            self.db_seeder.seed_data("BookShelf", [{"ShelfName": shelf_name, "LibrarianID": self.librarian_id}], 
                                     ["ShelfName", "LibrarianID"])
            
            # Get the newly created shelf ID
            shelf_records = self.db_seeder.get_all_records("BookShelf", self.librarian_id)
            for shelf_record in shelf_records:
                if shelf_record['ShelfName'] == shelf_name:
                    shelf_id = shelf_record['ShelfId']
                    break
        
        return shelf_id

    def _get_inserted_book_code(self):
        """Retrieve the BookCode of the newly inserted book"""
        conn, cursor = self.db_seeder.get_connection_and_cursor()
        try:
            cursor.execute("""
                SELECT BookCode FROM Book 
                WHERE BookTitle = ? AND ISBN = ? AND LibrarianID = ?
                ORDER BY BookCode DESC LIMIT 1
            """, (self.book_data['title'], self.book_data['isbn'], self.librarian_id))
            
            result = cursor.fetchone()
            if not result:
                raise Exception("Could not find the inserted book")
            
            return result[0]
        finally:
            conn.close()

    def _save_related_data(self, book_code, authors, genres):
        """Save author and genre records for the book"""
        # Insert author records
        if authors:
            author_data_list = [{'BookCode': book_code, 'bookAuthor': author.strip()} for author in authors]
            self.db_seeder.seed_data(tableName="BookAuthor", data=author_data_list, columnOrder=['BookCode', 'bookAuthor'])

        # Insert genre records
        if genres:
            genre_data_list = [{'BookCode': book_code, 'Genre': genre.strip()} for genre in genres]
            self.db_seeder.seed_data(tableName="Book_Genre", data=genre_data_list, columnOrder=['BookCode', 'Genre'])

    def _handle_save_success(self):
        """Handle successful book save"""
        # Refresh parent's books display
        if hasattr(self.parent, 'refresh_books_display'):
            self.parent.refresh_books_display()
        
        # Show success message and close dialog
        QMessageBox.information(self, "Success", f"Book '{self.book_data['title']}' has been added to the library!")
        self.accept()
            
    def _add_current_genre(self):
        """Add the current genre in the combobox to selected genres"""
        genre = self.genre_combo.currentText().strip()
        if genre and genre not in self.selected_genres:
            self.selected_genres.append(genre)
            self.update_genre_tags()
            self.genre_combo.clearEditText()
            QToolTip.showText(
                self.genre_combo.mapToGlobal(self.genre_combo.rect().bottomRight()),
                f"Added genre: {genre}",
                self.genre_combo,
                QRect(),
                1500)

    def create_genre_tag(self, genre):
        """Create a tag widget for a selected genre"""
        tag = QWidget()
        tag.setStyleSheet("QWidget { background-color: #f0f0f0; border: 1px solid #dbcfc1; border-radius: 10px; }")
        tag_layout = QHBoxLayout(tag)
        tag_layout.setContentsMargins(8, 2, 8, 2)
        tag_layout.setSpacing(5)
        
        label = QLabel(genre)
        label.setStyleSheet("background: transparent; border: none;")
        
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #5C4033; font-weight: bold; border: none;
            }
            QPushButton:hover { color: red; }
        """)
        remove_btn.clicked.connect(lambda: self.remove_genre(genre))
        
        tag_layout.addWidget(label)
        tag_layout.addWidget(remove_btn)
        return tag

    def update_genre_tags(self):
        """Update the genre tags display"""
        # Clear current tags
        for i in reversed(range(self.selected_genres_layout.count())):
            widget = self.selected_genres_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Add tags for each selected genre
        for genre in self.selected_genres:
            tag = self.create_genre_tag(genre)
            self.selected_genres_layout.addWidget(tag)

    def remove_genre(self, genre):
        """Remove a genre from selected genres"""
        if genre in self.selected_genres:
            self.selected_genres.remove(genre)
            self.update_genre_tags()
    
    def _add_current_genre_from_dropdown(self, index):
        """Add genre when selected from dropdown without needing Enter key"""
        if index >= 0:  # Ensure it's a valid selection
            genre = self.genre_combo.itemText(index)
            if genre and genre not in self.selected_genres:
                self.selected_genres.append(genre)
                self.update_genre_tags()
                # Clear the text but don't lose focus
                self.genre_combo.setCurrentText("")
                # Show tooltip confirmation
                QToolTip.showText(
                    self.genre_combo.mapToGlobal(self.genre_combo.rect().bottomRight()),
                    f"Added genre: {genre}",
                    self.genre_combo,
                    QRect(),
                    1500
                )
    
    def keyPressEvent(self, event):
        """Override key press events to prevent Enter from accepting the dialog"""
        from PySide6.QtCore import Qt, QEvent
        
        # If Enter/Return is pressed while the genre combo has focus
        if (event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter) and self.genre_combo.hasFocus():
            # Add the current genre instead of accepting the dialog
            self._add_current_genre()
            # Stop event propagation
            event.accept()
        else:
            # For all other keys, pass to parent handler
            super().keyPressEvent(event)
            
#MAIN WINDOW CLASS
class CollapsibleSidebar(QWidget):
    """Main library management window with sidebar navigation and book management features"""
    
    def __init__(self, librarian_id=None):
        super().__init__()
        
        # Initialize core properties
        self.librarian_id = librarian_id
        self.db_seeder = DatabaseSeeder()
        self.books_data = []
        self.original_books_data = []
        self.current_shelf = None
        self.current_shelf_id = None
        self.current_view = "books"
        
        # Set up window and UI
        self._setup_window()
        self._create_main_layout()
        self._initialize_navigation()
        
        # Load initial data
        self.load_books_from_database()

    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Library Management System")
        self.showMaximized()
        self.setStyleSheet("CollapsibleSidebar { background-color: #f1efe3; }")

    def _create_main_layout(self):
        """Create main content area and layout"""
        # Create main content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f5f3ed;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create and add main books view
        self.main_books_view = self._create_main_books_view()
        self.content_layout.addWidget(self.main_books_view)

    def _initialize_navigation(self):
        """Initialize navigation sidebar and main layout"""
        # Initialize navigation sidebar
        self.sidebar = NavigationSidebar()
        self.sidebar.on_navigation_clicked = nav_manager.handle_navigation
        
        # Combine sidebar and content area in main layout
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

    def load_books_from_database(self):
        """Load and process books data from database with related authors and genres"""
        try:
            # Retrieve data from all related tables using librarian ID for filtering
            books = self.db_seeder.get_all_records("Book", self.librarian_id or 1)
            book_authors = self.db_seeder.get_all_records("BookAuthor", self.librarian_id or 1)
            book_genres = self.db_seeder.get_all_records("Book_Genre", self.librarian_id or 1)
            book_shelf = self.db_seeder.get_all_records("BookShelf", self.librarian_id or 1)
            
            # Clear existing books data and process each book record
            self.books_data = []
            
            for book in books:
                try:
                    book_code = book.get("BookCode")
                    if not book_code:
                        continue
                    
                    # Get related data for this book
                    book_authors_list = [
                        author["bookAuthor"] for author in book_authors 
                        if author.get("BookCode") == book_code and author.get("bookAuthor")
                    ] or ["Unknown Author"]
                    
                    book_genres_list = [
                        genre["Genre"] for genre in book_genres 
                        if genre.get("BookCode") == book_code and genre.get("Genre")
                    ] or ["Unknown Genre"]
                    
                    # Find shelf name for the BookShelf ID
                    shelf_name = self._get_shelf_name(book.get("BookShelf"), book_shelf)
                    
                    # Create book data dictionary
                    book_data = {
                        "book_code": book_code,
                        "title": book.get("BookTitle", "Unknown Title"),
                        "author": book_authors_list,
                        "genre": book_genres_list,
                        "isbn": book.get("ISBN", ""),
                        "publisher": book.get("Publisher", "Unknown Publisher"), 
                        "description": book.get("BookDescription", ""),
                        "shelf": shelf_name,
                        "copies": book.get("BookTotalCopies", 0),
                        "available_copies": book.get("BookAvailableCopies", 0),
                        "image": book.get("BookCover", "")
                    }
                    
                    self.books_data.append(book_data)
                    
                except Exception as e:
                    continue
            
            # Store original data for search functionality
            self.original_books_data = self.books_data.copy()
            
            # Populate the display if grid layout exists
            if hasattr(self, 'grid_layout'):
                self.populate_books()
                
        except Exception as e:
            # Initialize with empty data if there's an error
            self.books_data = []
            self.original_books_data = []

    def _get_shelf_name(self, book_shelf_id, book_shelf_records):
        """Get shelf name from shelf ID"""
        shelf_name = ""
        if book_shelf_id:
            try:
                book_shelf_id_int = int(book_shelf_id)
            except (ValueError, TypeError):
                book_shelf_id_int = None
                
            for shelf in book_shelf_records:
                shelf_id = shelf.get("ShelfId")
                if shelf_id == book_shelf_id_int or str(shelf_id) == str(book_shelf_id):
                    shelf_name = shelf.get("ShelfName", "")
                    break
        return shelf_name
    
    #SORTING BOOKS 
    def show_sort_options(self):
        """Show a popup menu with sorting options"""
        sort_menu = QMenu(self)
        sort_menu.setStyleSheet("""
            QMenu {
                background-color: #FFFEF0; border: 2px solid #5C4033; border-radius: 8px; padding: 5px;
            }
            QMenu::item { padding: 8px 20px; color: #5C4033; font-size: 14px; }
            QMenu::item:selected { background-color: #dbcfc1; border-radius: 4px; }
        """)
        
        # Add sort options
        sort_options = [
            ("Title (A-Z)", "title", True), ("Title (Z-A)", "title", False),
            ("Author (A-Z)", "author", True), ("Author (Z-A)", "author", False),
            ("Most Copies", "copies", False), ("Least Copies", "copies", True)
        ]
        
        for label, key, ascending in sort_options:
            sort_menu.addAction(label, lambda k=key, a=ascending: self.sort_books(k, a))
        
        # Show menu at button position
        sort_menu.exec(self.sort_button.mapToGlobal(self.sort_button.rect().bottomLeft()))

    def sort_books(self, key, ascending=True):
        """Sort books by the given key using database sorting"""
        try:
            # Map the sorting parameters to the database filter names
            filter_map = {
                ("title", True): "ascendingTitle", ("title", False): "descendingTitle", 
                ("author", True): "ascendingAuthor", ("author", False): "descendingAuthor",
                ("copies", False): "mostCopies", ("copies", True): "leastCopies"
            }
            
            filter_name = filter_map.get((key, ascending))
            if not filter_name:
                return
            
            # Get sorted books from database
            sorted_books = self.db_seeder.filterBooks(filter_name, self.librarian_id or 1)
            
            if not sorted_books:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Sort Books", "No books found to sort.")
                return
            
            # Process the sorted books data
            self.books_data = self._process_book_records(sorted_books)
            
            # Update the title to show current sort
            sort_descriptions = {
                "ascendingTitle": "Title (A-Z)", "descendingTitle": "Title (Z-A)",
                "ascendingAuthor": "Author (A-Z)", "descendingAuthor": "Author (Z-A)",
                "mostCopies": "Most Copies", "leastCopies": "Least Copies"
            }
            
            current_sort = sort_descriptions.get(filter_name, "Books Management")
            self.title_label.setText(f"Sorted by {current_sort}")
            
            # Refresh the display with sorted books
            self.populate_books()
            
        except Exception:
            pass

    def _process_book_records(self, book_records):
        """Helper method to process book records from database into UI format"""
        book_authors = self.db_seeder.get_all_records("BookAuthor", self.librarian_id or 1)
        book_genres = self.db_seeder.get_all_records("Book_Genre", self.librarian_id or 1)
        book_shelf = self.db_seeder.get_all_records("BookShelf", self.librarian_id or 1)
        
        processed_books = []
        for book in book_records:
            try:
                book_code = book.get("BookCode")
                if not book_code:
                    continue
                
                # Get related data for this book
                book_authors_list = [
                    author["bookAuthor"] for author in book_authors 
                    if author.get("BookCode") == book_code and author.get("bookAuthor")
                ] or ["Unknown Author"]
                
                book_genres_list = [
                    genre["Genre"] for genre in book_genres 
                    if genre.get("BookCode") == book_code and genre.get("Genre")
                ] or ["Unknown Genre"]
                
                # Find shelf name
                shelf_name = self._get_shelf_name(book.get("BookShelf"), book_shelf)
                
                # Create book data dictionary
                book_data = {
                    "book_code": book_code,
                    "title": book.get("BookTitle", "Unknown Title"),
                    "author": book_authors_list,
                    "genre": book_genres_list,
                    "isbn": book.get("ISBN", ""),
                    "publisher": book.get("Publisher", "Unknown Publisher"), 
                    "description": book.get("BookDescription", ""),
                    "shelf": shelf_name,
                    "copies": book.get("BookTotalCopies", 0),
                    "available_copies": book.get("BookAvailableCopies", 0),
                    "image": book.get("BookCover", "")
                }
                
                processed_books.append(book_data)
                
            except Exception:
                continue
        
        return processed_books

    def show_shelf_view(self):
        """Show books organized by shelf location"""
        shelf_menu = QMenu(self)
        shelf_menu.setStyleSheet("""
            QMenu {
                background-color: #FFFEF0; border: 2px solid #5C4033; border-radius: 8px; padding: 5px;
            }
            QMenu::item { padding: 8px 20px; color: #5C4033; font-size: 14px; }
            QMenu::item:selected { background-color: #dbcfc1; border-radius: 4px; }
        """)
        
        # Get available shelves from database
        shelf_records = []
        try:
            bookshelf_records = self.db_seeder.get_all_records("BookShelf", self.librarian_id or 1)
            shelf_records = [(row["ShelfId"], row["ShelfName"]) for row in bookshelf_records 
                           if "ShelfName" in row and row["ShelfName"] and "ShelfId" in row]
            shelf_records = sorted(shelf_records, key=lambda x: x[1])
        except Exception:
            shelf_records = []

        # Add menu options
        shelf_menu.addAction("All Books", lambda: self.display_shelf_books(None, None))
        shelf_menu.addAction("No Shelf", lambda: self.display_shelf_books("No Shelf", None))
        
        if shelf_records:
            shelf_menu.addSeparator()
            for shelf_id, shelf_name in shelf_records:
                shelf_menu.addAction(f"Shelf {shelf_name}", 
                                   lambda sid=shelf_id, sname=shelf_name: self.display_shelf_books(sname, sid))
        else:
            no_shelves_action = shelf_menu.addAction("No shelves found")
            no_shelves_action.setEnabled(False)

        # Show menu at button position
        shelf_menu.exec(self.shelf_button.mapToGlobal(self.shelf_button.rect().bottomLeft()))

    def display_shelf_books(self, shelf=None, shelf_id=None):
        """Display books for a specific shelf or all books if shelf is None"""
        if shelf is None:
            # Show all books - reload from database
            self.current_shelf = None
            self.current_shelf_id = None
            self.delete_shelf_button.hide()
            self.load_books_from_database()
            self.title_label.setText("Books Management")
        else:
            self.current_shelf = shelf
            self.current_shelf_id = shelf_id
            self.delete_shelf_button.show()
            
            # Filter books by shelf using database
            try:
                shelf_books = self.db_seeder.filterBooks(shelf, self.librarian_id or 1)
                
                if not shelf_books:
                    self.books_data = []
                    self._handle_empty_shelf(shelf)
                    return
                
                # Process the filtered books data
                self.books_data = self._process_book_records(shelf_books)
                
                # Set title based on shelf type
                if shelf == "No Shelf":
                    self.title_label.setText("Books without Shelf Assignment")
                else:
                    self.title_label.setText(f"Books on Shelf {shelf}")
                
            except Exception:
                self.books_data = []
                if shelf == "No Shelf":
                    self.title_label.setText("Books without Shelf Assignment")
                else:
                    self.title_label.setText(f"Books on Shelf {shelf}")
        
        # Update display
        self.populate_books()

    def _handle_empty_shelf(self, shelf):
        """Handle display when shelf is empty"""
        if shelf == "No Shelf":
            self.title_label.setText("Books without Shelf Assignment")
            message_text = "No books are currently unassigned to shelves.\n\nBooks without shelf assignments will appear here."
        else:
            self.title_label.setText(f"Books on Shelf {shelf}")
            message_text = f"Shelf '{shelf}' is empty.\n\nTo add books to this shelf, use the '➕ Add Book' option and assign them to shelf '{shelf}'."
        
        self.populate_books()
        
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle("Shelf View")
        msg.setText(message_text)
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox { background-color: white; color: black; font-weight: normal; }
            QLabel { color: black; font-weight: normal; font-size: 14px; background-color: transparent; border: none; }
            QPushButton { background-color: #5C4033; color: white; padding: 5px 15px; border: none; border-radius: 5px; font-weight: normal; }
            QPushButton:hover { background-color: #8B4513; }
        """)
        msg.exec()

    def delete_current_shelf(self):
        """Delete the currently selected shelf"""
        from PySide6.QtWidgets import QMessageBox

        shelf = self.current_shelf
        shelf_id = self.current_shelf_id
        
        if not shelf or not shelf_id:
            QMessageBox.warning(self, "Error", "No shelf selected for deletion.")
            return

        confirm = QMessageBox.question(
            self, "Delete Shelf",
            f"Are you sure you want to delete shelf '{shelf}'?\nAll books on this shelf will remain, but the shelf will be removed from the list.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if confirm == QMessageBox.Yes:
            try:
                # Use ShelfId for deletion
                self.db_seeder.delete_table(tableName="BookShelf", column="ShelfId", value=shelf_id, librarian_id=self.librarian_id or 1)
                QMessageBox.information(self, "Success", f"Shelf '{shelf}' deleted.")
                self.current_shelf = None
                self.current_shelf_id = None
                self.delete_shelf_button.hide()
                self.load_books_from_database()
                self.title_label.setText("Books Management")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete shelf: {e}")

    def _create_main_books_view(self):
        """Create the main books view with search and grid"""
        view_widget = QWidget()
        view_layout = QVBoxLayout(view_widget)
        view_layout.setContentsMargins(40, 50, 40, 50)
        
        # Create header section with title and controls
        header_layout = QHBoxLayout()
        
        # Create title label
        self.title_label = QLabel("Books Management")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #5C4033; font-size: 50px; font-weight: bold; background-color: transparent;
                padding: 0px; margin: 0px;
            }
        """)
        
        # Create search and control buttons container
        search_container = self._create_search_container()
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(search_container, alignment=Qt.AlignTop)
        
        view_layout.addLayout(header_layout)
        view_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Create books section
        self.books_container = self._create_books_section()
        view_layout.addWidget(self.books_container)
        
        view_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        return view_widget

    def _create_search_container(self):
        """Create search bar and control buttons container"""
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        # Create delete shelf button (hidden by default)
        self.delete_shelf_button = QPushButton("🗑️")
        self.delete_shelf_button.setFixedSize(50, 50)
        self.delete_shelf_button.setToolTip("Delete This Shelf")
        self.delete_shelf_button.clicked.connect(self.delete_current_shelf)
        self.delete_shelf_button.setStyleSheet("""
            QPushButton {
                color: #CC4125; font-size: 20px; font-weight: bold; background-color: #F5F5F5;
                border: 3px solid #CC4125; border-radius: 10px;
            }
            QPushButton:hover { background-color: #CC4125; color: white; }
        """)
        self.delete_shelf_button.hide()
        
        # Create search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search books...")
        self.search_bar.setFixedSize(300, 50)
        self.search_bar.returnPressed.connect(self.perform_search)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                color: #5C4033; font-size: 16px; padding: 10px 15px; background-color: #FFFEF0;
                border: 3px solid #5C4033; border-radius: 10px;
            }
            QLineEdit:focus { border-color: #8B4513; background-color: white; }
        """)
        self.search_bar.textChanged.connect(self.perform_search)

        # Create control buttons
        button_style = """
            QPushButton {
                color: #5C4033; font-size: 20px; font-weight: bold; background-color: #F5F5F5;
                border: 3px solid #5C4033; border-radius: 10px;
            }
            QPushButton:hover { background-color: #5C4033; color: white; }
        """
        
        # Control buttons configuration: (text, tooltip, callback)
        buttons_config = [
            ("🔍", None, self.perform_search),
            ("🔄", "Sort Books", self.show_sort_options),
            ("📚", "View by Shelf", self.show_shelf_view),
            ("➕", None, self.show_add_options)
        ]
        
        # Create buttons
        buttons = []
        for text, tooltip, callback in buttons_config:
            button = QPushButton(text)
            button.setFixedSize(50, 50)
            if tooltip:
                button.setToolTip(tooltip)
            button.clicked.connect(callback)
            button.setStyleSheet(button_style)
            buttons.append(button)
        
        # Store button references
        self.search_button, self.sort_button, self.shelf_button, self.add_button = buttons
        
        # Add all widgets to layout
        search_layout.addWidget(self.delete_shelf_button)
        search_layout.addWidget(self.search_bar)
        for button in buttons:
            search_layout.addWidget(button)
        
        return search_container
    
    def show_add_options(self):
        """Show dropdown menu with Add Book and Add Shelf options"""
        add_menu = QMenu(self)
        add_menu.setStyleSheet("""
            QMenu {
                background-color: #FFFEF0; border: 2px solid #5C4033; border-radius: 8px; padding: 5px;
            }
            QMenu::item { padding: 8px 20px; color: #5C4033; font-size: 14px; }
            QMenu::item:selected { background-color: #dbcfc1; border-radius: 4px; }
        """)
        
        # Add options
        add_menu.addAction("Add Book", self.show_add_book_dialog)
        add_menu.addAction("Add Shelf", self.show_add_shelf_dialog)
        
        # Show menu at button position
        add_menu.exec(self.add_button.mapToGlobal(self.add_button.rect().bottomLeft()))

    def show_add_shelf_dialog(self):
        """Show dialog to add a new bookshelf"""
        # Create the add shelf dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Shelf")
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet("""
            QDialog { background-color: #f1efe3; }
            QLabel { color: #5C4033; font-size: 16px; font-weight: bold; }
            QLineEdit {
                background-color: white; border: 2px solid #dbcfc1; border-radius: 8px;
                padding: 10px; font-size: 14px; color: #5C4033;
            }
            QLineEdit:focus { border-color: #5C4033; }
            QPushButton { padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: bold; }
        """)
        
        # Dialog layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title and input section
        title_label = QLabel("Add New Bookshelf")
        title_label.setStyleSheet("font-size: 20px; margin-bottom: 30px;")
        layout.addWidget(title_label)
        
        input_container = QVBoxLayout()
        shelf_label = QLabel("Shelf ID:")
        input_container.addWidget(shelf_label)
        
        shelf_input = QLineEdit()
        shelf_input.setPlaceholderText("Select BookShelf ")
        input_container.addWidget(shelf_input)
        
        help_label = QLabel("Shelf ID must be one letter (A-Z) followed by 1-5 digits")
        help_label.setStyleSheet("color: #666; font-weight: normal; font-size: 12px;")
        input_container.addWidget(help_label)
        
        layout.addLayout(input_container)
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Shelf")
        save_btn.setStyleSheet("background-color: #5C4033; color: white; min-width: 100px;")
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("background-color: white; color: #5C4033; border: 2px solid #5C4033; min-width: 100px;")
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Connect button signals
        cancel_btn.clicked.connect(dialog.reject)
        save_btn.clicked.connect(lambda: self.save_new_shelf(dialog, shelf_input.text()))
        
        # Show dialog
        dialog.exec()

    def save_new_shelf(self, dialog, shelf_id):
        """Save a new bookshelf to the database"""
        shelf_id = shelf_id.strip()
        
        # Validate shelf ID format using utility function
        if not validate_shelf_format(shelf_id):
            self._show_validation_message(dialog, "Shelf ID must be one letter (A-Z) followed by 1-5 digits.\nExample: A1, B12, C345")
            return
        
        try:
            # Check for duplicate shelf
            exist = self.db_seeder.handleDuplication(tableName="BookShelf", librarianID=self.librarian_id, column="ShelfName", value=shelf_id)               
            
            if not exist:
                self._show_validation_message(dialog, f"Shelf ID '{shelf_id}' already exists.")
                return
            
            # Insert new shelf into database
            try:
                self.db_seeder.seed_data(
                    tableName="BookShelf",
                    data=[{"ShelfName": shelf_id, "LibrarianID": self.librarian_id or 1}], 
                    columnOrder=["ShelfName", "LibrarianID"]
                )
                
                # Verify insertion
                conn, cursor = self.db_seeder.get_connection_and_cursor()
                cursor.execute("SELECT * FROM BookShelf WHERE ShelfName = ? AND LibrarianID = ?", 
                            (shelf_id, self.librarian_id or 1))
                verification = cursor.fetchone()
                conn.close()
                
                if not verification:
                    raise Exception("Shelf was not properly inserted into database")
                
            except Exception as db_error:
                raise db_error
            
            # Show success message
            self._show_success_message(dialog, shelf_id)
            dialog.accept()
            
        except Exception as e:
            self._show_error_message(dialog, f"Failed to add shelf: {str(e)}")

    def _show_validation_message(self, parent, message):
        """Show validation error message"""
        msg = QMessageBox(parent)
        msg.setWindowTitle("Validation Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Warning)
        msg.setStyleSheet(self._get_message_box_style())
        msg.exec()

    def _show_success_message(self, parent, shelf_id):
        """Show success message for shelf creation"""
        success_msg = QMessageBox(parent)
        success_msg.setWindowTitle("Success")
        success_msg.setText(f"Shelf '{shelf_id}' has been added successfully!\n\nYou can now find it in the 'View by Shelf' menu (📚 button) to sort books by this shelf.")
        success_msg.setIcon(QMessageBox.Information)
        success_msg.setStyleSheet("""
            QMessageBox { background-color: white; color: black; font-weight: normal; }
            QLabel { color: black; font-weight: normal; font-size: 14px; background-color: transparent; border: none; }
            QPushButton { background-color: #5C4033; color: white; padding: 5px 15px; border: none; border-radius: 5px; font-weight: normal; }
            QPushButton:hover { background-color: #8B4513; }
        """)
        success_msg.exec()

    def _show_error_message(self, parent, message):
        """Show error message"""
        msg = QMessageBox(parent)
        msg.setWindowTitle("Error")
        msg.setText(message)
        msg.setIcon(QMessageBox.Critical)
        msg.setStyleSheet(self._get_message_box_style())
        msg.exec()

    def _get_message_box_style(self):
        """Get standard message box styling"""
        return """
            QMessageBox { background-color: white; color: black; font-weight: normal; }
            QLabel { color: black; font-weight: normal; font-size: 14px; background-color: transparent; border: none; }
            QPushButton { background-color: #e0e0e0; color: black; padding: 5px 15px; border: 1px solid #bbbbbb; border-radius: 5px; font-weight: normal; }
            QPushButton:hover { background-color: #d0d0d0; }
        """
            
    def perform_search(self):
        """Perform search based on search bar text"""
        search_text = self.search_bar.text().strip()
        
        if search_text:
            # Search using database
            try:
                search_results = self.db_seeder.search_records("Book", search_text, self.librarian_id or 1)
                self.books_data = [self._format_book_for_ui(book) for book in search_results]
            except Exception:
                # Fallback to local search if database fails
                self._perform_local_search(search_text)
        else:
            # Restore all books when search is cleared
            self.load_books_from_database()
        
        self.populate_books()

    def _format_book_for_ui(self, book):
        """Format database book record for UI display"""
        try:
            # Get related data
            book_authors = self.db_seeder.get_all_records("BookAuthor", self.librarian_id or 1)
            book_genres = self.db_seeder.get_all_records("Book_Genre", self.librarian_id or 1)
            book_shelf = self.db_seeder.get_all_records("BookShelf", self.librarian_id or 1)
            
            book_code = book.get("BookCode", "")
            
            # Get authors and genres for this book
            authors = [
                author["bookAuthor"] for author in book_authors 
                if author.get("BookCode") == book_code and author.get("bookAuthor")
            ] or ["Unknown Author"]
            
            genres = [
                genre["Genre"] for genre in book_genres 
                if genre.get("BookCode") == book_code and genre.get("Genre")
            ] or ["Unknown Genre"]
            
            # Get shelf name
            shelf_name = self._get_shelf_name(book.get("BookShelf"), book_shelf)
            
            return {
                "book_code": book_code,
                "title": book.get("BookTitle", "Unknown Title"),
                "author": authors,
                "genre": genres,
                "isbn": book.get("ISBN", ""),
                "publisher": book.get("Publisher", "Unknown Publisher"),
                "description": book.get("BookDescription", ""),
                "shelf": shelf_name,
                "copies": book.get("BookTotalCopies", 0),
                "available_copies": book.get("BookAvailableCopies", 0),
                "image": book.get("BookCover", "")
            }
        except Exception:
            return {}

    def _perform_local_search(self, search_text):
        """Fallback local search through existing books data"""
        search_text = search_text.lower()
        filtered_books = []
        
        for book in self.original_books_data:
            # Check if search text matches any book field
            if self._book_matches_search(book, search_text):
                filtered_books.append(book)
        
        self.books_data = filtered_books

    def _book_matches_search(self, book, search_text):
        """Check if book matches search criteria"""
        # Search in title
        if search_text in book['title'].lower():
            return True
        
        # Search in authors
        if self._search_in_list_field(book.get('author', []), search_text):
            return True
        
        # Search in genres  
        if self._search_in_list_field(book.get('genre', []), search_text):
            return True
        
        # Search in ISBN
        if search_text in str(book.get('isbn', '')).lower():
            return True
        
        return False

    def _search_in_list_field(self, field_value, search_text):
        """Search for text in a field that can be a list or string"""
        if isinstance(field_value, list):
            return any(search_text in item.lower() for item in field_value)
        return search_text in str(field_value).lower()

    def _create_books_section(self):
        """Create the books display section with multiple columns and vertical scrolling"""
        books_container = QWidget()
        books_container.setMinimumWidth(1200)
        books_container.setMinimumHeight(590)
        books_container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #dbcfc1;
            }
        """)
        
        books_layout = QVBoxLayout(books_container)
        books_layout.setContentsMargins(20, 20, 20, 20)
        books_layout.setSpacing(15)
        
        books_title = QLabel("Available Books")
        books_title.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 24px;
                font-weight: bold;
                padding: 10px 0px;
                border: none;
                background-color: transparent;
            }
        """)
        books_layout.addWidget(books_title)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background-color: #f0f0f0;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #5C4033;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #8B4513;
            }
        """)
        
        # Create scrollable content widget
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: transparent;")
          # Use grid layout with multiple columns
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(15)
        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        
        for i in range(6):  
            self.grid_layout.setColumnStretch(i, 1)   
        
        scroll_area.setWidget(self.scroll_content)
        books_layout.addWidget(scroll_area)
        
        return books_container
    
    def populate_books(self):
        """Populate the books grid layout with book cards"""
        # Clear existing book card widgets from the grid
        self._clear_grid_layout()
        
        # Add book cards to grid layout (6 books per row)
        columns_per_row = 6
        for index, book in enumerate(self.books_data):
            row = index // columns_per_row
            col = index % columns_per_row            
            
            book_card = self.create_book_card(book)
            self.grid_layout.addWidget(book_card, row, col)

    def _clear_grid_layout(self):
        """Clear all widgets from the grid layout"""
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
    
    def create_book_card(self, book_data):
        """Create a clickable book card widget with cover, title, and author"""
        # Create main card button widget
        card_widget = QPushButton()
        card_widget.setFixedSize(200, 280)
        card_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Connect click event and apply styling
        card_widget.clicked.connect(lambda checked, data=book_data: self.show_book_preview(data))
        card_widget.setStyleSheet(self._get_book_card_style())
        
        # Create card layout and content
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(10, 10, 10, 8)
        card_layout.setSpacing(8)
        
        # Add book cover, title, and author
        book_cover = self._create_book_cover(book_data)
        title_label = self._create_book_title_label(book_data["title"])
        author_label = self._create_book_author_label(book_data["author"])
        
        card_layout.addWidget(book_cover, alignment=Qt.AlignCenter)
        card_layout.addWidget(title_label)
        card_layout.addWidget(author_label)
        
        return card_widget

    def _get_book_card_style(self):
        """Get book card styling"""
        return """
            QPushButton {
                background-color: #f8f8f8; border-radius: 12px; border: 2px solid #e0e0e0; text-align: center;
            }
            QPushButton:hover { background-color: #f0f0f0; border-color: #5C4033; }
            QPushButton:pressed { background-color: #e8e8e8; }
        """

    def _create_book_cover(self, book_data):
        """Create book cover image widget"""
        book_cover = QLabel()
        book_cover.setFixedSize(150, 200)
        book_cover.setAlignment(Qt.AlignCenter)
        book_cover.setStyleSheet("""
            QLabel { background-color: #dbcfc1; border-radius: 8px; border: 2px solid #5C4033; }
        """)
        
        # Load book cover image using shared utility function
        image_path = book_data.get("image", "")
        pixmap = load_pixmap_safely(image_path, QSize(150, 200))
        
        if pixmap and not pixmap.isNull():
            book_cover.setPixmap(pixmap)
            book_cover.setStyleSheet("QLabel { border-radius: 8px; border: 2px solid #5C4033; }")
        
        return book_cover

    def _create_book_title_label(self, title):
        """Create book title label"""
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(35)
        title_label.setStyleSheet("""
            QLabel {
                color: #5C4033; font-size: 14px; font-weight: bold; background-color: transparent;
                border: none; padding: 2px;
            }
        """)
        return title_label

    def _create_book_author_label(self, authors):
        """Create book author label"""
        author_text = format_authors_display(authors)
        author_label = QLabel(author_text)
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setWordWrap(True)
        author_label.setMaximumHeight(25)
        author_label.setStyleSheet("""
            QLabel {
                color: #8B4513; font-size: 12px; background-color: transparent;
                border: none; padding: 1px;
            }
        """)
        return author_label 
    
    def show_book_preview(self, book_data):
        """Show book preview dialog"""
        preview_dialog = BookPreviewDialog(book_data, self)
        preview_dialog.exec()
    
    def open_book_edit(self, book_data):
        """Open the book edit view"""
        self._clear_content_layout()
        self.book_edit_view = BookEditView(book_data, self)
        self.content_layout.addWidget(self.book_edit_view)
        self.current_view = "edit"
    
    def show_books_view(self):
        """Show the main books view"""
        self._clear_content_layout()
        self.load_books_from_database()
        self.content_layout.addWidget(self.main_books_view)
        self.current_view = "books"
    
    def show_book_edit_view(self, book_data):
        """Show the book edit view in the main window"""
        try:
            self._clear_content_layout()
            edit_view = BookEditView(book_data, self)
            self.content_layout.addWidget(edit_view)
            self.current_view = "edit"
        except Exception:
            pass

    def _clear_content_layout(self):
        """Clear all widgets from the content layout"""
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def refresh_books_display(self):
        """Refresh the books display"""
        self.load_books_from_database()

    def show_add_book_dialog(self):
        """Show the book add dialog"""
        dialog = AddBookDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_books_from_database()
