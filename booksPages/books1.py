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

class BookPreviewDialog(QDialog):
    def __init__(self, book_data, parent=None):
        super().__init__(parent)
        self.book_data = book_data
        self.parent_window = parent
        self.setWindowTitle(f"Book Preview - {book_data['title']}")
        self.setFixedSize(900, 750)
        self.setStyleSheet("""QDialog {background-color: #f1efe3;} """)
        self.init_ui()
      
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Header with book title
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(10, 5, 10, 5)
        
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
          # Main content area
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
        
        # Left side - Book cover
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
        
        # Load book cover if available
        image_path = self.book_data.get("image", "")
        if image_path and isinstance(image_path, str) and os.path.exists(image_path):
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        QSize(200, 280),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    self.cover_label.setPixmap(scaled_pixmap)
                    self.cover_label.setStyleSheet("""
                        QLabel {
                            border: 2px solid #dbcfc1;
                            border-radius: 12px;
                        }
                    """)
                else:
                    self.cover_label.setText("No Cover Available")
            except Exception as e:
                self.cover_label.setText("Cover Load Error")
        else:
            self.cover_label.setText("No Cover Available")
        
        left_layout.addWidget(self.cover_label, 0, Qt.AlignCenter)
        left_layout.addStretch()
          # Right side - Book details
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(10, 10, 10, 10)
        right_layout.setSpacing(15)
        
        # Book information
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
        
        # Author(s)
        authors = self.book_data.get('author', [])
        if isinstance(authors, list):
            author_text = ', '.join(authors)
        else:
            author_text = str(authors)
        
        author_label = QLabel(f"<b>Author:</b> {author_text}")
        author_label.setStyleSheet(info_style)
        author_label.setWordWrap(True)
        right_layout.addWidget(author_label)
        
        # Genre(s)
        genres = self.book_data.get('genre', [])
        if isinstance(genres, list):
            genre_text = ', '.join(genres)
        else:
            genre_text = str(genres)
        
        genre_label = QLabel(f"<b>Genre:</b> {genre_text}")
        genre_label.setStyleSheet(info_style)
        genre_label.setWordWrap(True)
        right_layout.addWidget(genre_label)
        
        # ISBN
        isbn = self.book_data.get('isbn', 'N/A')
        isbn_label = QLabel(f"<b>ISBN:</b> {isbn}")
        isbn_label.setStyleSheet(info_style)
        right_layout.addWidget(isbn_label)
        
        # Shelf location
        shelf = self.book_data.get('shelf', 'N/A')
        shelf_label = QLabel(f"<b>Shelf:</b> {shelf}")
        shelf_label.setStyleSheet(info_style)
        right_layout.addWidget(shelf_label)
        
        # Copies information
        total_copies = self.book_data.get('copies', 0)
        available_copies = self.book_data.get('available_copies', 0)
        copies_label = QLabel(f"<b>Copies:</b> {available_copies} available of {total_copies} total")
        copies_label.setStyleSheet(info_style)
        right_layout.addWidget(copies_label)
          # Description
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
        
        # Button layout
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
                border: 2px solid #5C4033;                border-radius: 16px;
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
        self.accept()  # Close the preview dialog
        if self.parent_window:
            self.parent_window.show_book_edit_view(self.book_data)
        else:  print("[ERROR] parent_window is None!")

class BookEditView(QWidget):
    def __init__(self, book_data, parent_window):
        super().__init__()
        self.book_data = book_data 
        self.parent_window = parent_window
        # Initialize database seeder
        from tryDatabase import DatabaseSeeder
        self.db_seeder = DatabaseSeeder()
        self.init_ui()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        header_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Back to Books")
        back_btn.setFixedSize(150, 40)
        back_btn.clicked.connect(self.go_back)
        back_btn.setStyleSheet("""
            QPushButton {
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 2px solid #5C4033;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        header_layout.addWidget(back_btn)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        title = QLabel(f"Edit Book: {self.book_data['title']}")
        title.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 30px;
                font-weight: bold;
                padding: 10px 0px;
            }
        """)
        layout.addWidget(title)
        
        form_widget = QWidget()
        form_widget.setStyleSheet("""            QWidget {
                background-color: white;
                border-radius: 16px;
                border: 2px solid #dbcfc1;
            }
        """)
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        self.title_input = QLineEdit(self.book_data.get('title', ''))
        self.title_input.setReadOnly(True)
        self.title_input.setStyleSheet(self.get_readonly_input_style())
          # Handle author - could be a string or a list from the database
        author = self.book_data.get('author', '')
        if isinstance(author, list):
            author = ', '.join(author)
        self.author_input = QLineEdit(author)
        self.author_input.setReadOnly(True)
        self.author_input.setStyleSheet(self.get_readonly_input_style())
        
        # Handle genre - could be a string or a list from the database
        genre = self.book_data.get('genre', '')
        if isinstance(genre, list):
            genre = ', '.join(genre)
        self.genre_input = QLineEdit(genre)
        self.genre_input.setReadOnly(True)
        self.genre_input.setStyleSheet(self.get_readonly_input_style())
          # Ensure ISBN is a string
        isbn = self.book_data.get('isbn', '')
        self.isbn_input = QLineEdit(str(isbn))
        self.isbn_input.setReadOnly(True)
        self.isbn_input.setStyleSheet(self.get_readonly_input_style())
        
        # Ensure copies is a string
        copies = self.book_data.get('copies', 1)
        self.copies_input = QLineEdit(str(copies))
        self.copies_input.setStyleSheet(self.get_editable_input_style())
        
        # Create shelf dropdown instead of text input
        self.shelf_input = QComboBox()
        self.shelf_input.setEditable(False)  
        self.shelf_input.setStyleSheet("""
            QComboBox {
                color: #5C4033;
                font-size: 16px;
                padding: 10px;
                background-color: white;
                border: 2px solid #dbcfc1;
                border-radius: 10px;
            }
            QComboBox:focus {
                border-color: #5C4033;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 1px solid #5C4033;
                width: 10px;
                height: 10px;
                background-color: #5C4033;
            }
        """)
        
        # Populate shelf dropdown with available shelves from database
        try:  
            # Get librarian_id from parent window
            librarian_id = getattr(self.parent_window, 'librarian_id', 1)
            shelf_records = self.db_seeder.get_all_records("BookShelf", librarian_id)
            # Extract ShelfId values from records, skipping any missing or null ones
            available_shelves = [record['ShelfId'] for record in shelf_records if record.get('ShelfId')] 
            
            # If no shelves exist for this librarian, create default shelf A1
            if not available_shelves:
                print(f"📚 BookEditView - No shelves found, creating default shelf A1")
                try:
                    self.db_seeder.seed_data("BookShelf", [{"ShelfId": "A1", "LibrarianID": librarian_id}], ["ShelfId", "LibrarianID"])
                    available_shelves = ["A1"]
                    print(f"📚 BookEditView - Created default shelf A1")
                except Exception as seed_error:
                    print(f"⚠️ Could not create default shelf: {seed_error}")
                    available_shelves = ["A1"]  # Use A1 anyway
            
            # Add all available shelves to dropdown
            self.shelf_input.addItems(available_shelves)
            print(f"📚 BookEditView - Added shelves to dropdown: {available_shelves}")

            # Set current shelf value if it exists
            current_shelf = self.book_data.get('shelf', '')
            print(f"📚 BookEditView - Current shelf from book_data: '{current_shelf}'")
            
            if current_shelf:
                index = self.shelf_input.findText(current_shelf)
                print(f"📚 BookEditView - Found shelf '{current_shelf}' at index: {index}")
                
                if index >= 0:
                    self.shelf_input.setCurrentIndex(index)
                    print(f"📚 BookEditView - Set dropdown to index {index}")
                else:
                    # If current shelf is not in the list, add it and select it
                    print(f"📚 BookEditView - Shelf '{current_shelf}' not found in dropdown, adding it")
                    # Add the shelf to the end of the dropdown
                    self.shelf_input.addItem(current_shelf)
                    index = self.shelf_input.findText(current_shelf)
                    if index >= 0:
                        self.shelf_input.setCurrentIndex(index)
                        print(f"📚 BookEditView - Added and set shelf '{current_shelf}' at index {index}")
            else:
                # No current shelf, select first available shelf
                if available_shelves:
                    self.shelf_input.setCurrentIndex(0)
                    print(f"📚 BookEditView - No current shelf, set to first available: {available_shelves[0]}")
                    
        except Exception as e:
            print(f"❌ Error loading shelves in BookEditView: {e}")
            print(f"📚 BookEditView - Exception traceback:")
            import traceback
            traceback.print_exc()
            # Fallback to A1
            self.shelf_input.addItem("A1")
            self.shelf_input.setCurrentIndex(0)
            print(f"📚 BookEditView - Fallback: Added A1 shelf")
        
        self.description_input = QTextEdit(self.book_data.get('description', 'No description available'))
        self.description_input.setMaximumHeight(150)
        self.description_input.setStyleSheet("""
            QTextEdit {
                color: #5C4033;
                font-size: 15px;
                padding: 10px;
                background-color: white;
                border: 2px solid #dbcfc1;
                border-radius: 16px;
            }
            QTextEdit:focus {
                border-color: #5C4033;            }
        """)
        
        form_layout.addRow(self.create_label("Title:"), self.title_input)
        form_layout.addRow(self.create_label("Author:"), self.author_input)
        form_layout.addRow(self.create_label("Genre:"), self.genre_input)
        form_layout.addRow(self.create_label("ISBN:"), self.isbn_input)
        form_layout.addRow(self.create_label("Available copy of books:"), self.copies_input)
        form_layout.addRow(self.create_label("Shelf No.:"), self.shelf_input)
        form_layout.addRow(self.create_label("Description:"), self.description_input)
        layout.addWidget(form_widget)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save Changes")
        save_btn.setFixedSize(150, 50)
        save_btn.clicked.connect(self.save_changes)
        save_btn.setStyleSheet("""
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
        
        # Delete button
        delete_btn = QPushButton("Delete Book")
        delete_btn.setFixedSize(150, 50)
        delete_btn.clicked.connect(self.delete_book)
        delete_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 16px;
                font-weight: bold;
                background-color: #CC4125;
                border: none;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #E55B4A;
            }
        """)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(150, 50)
        cancel_btn.clicked.connect(self.go_back)
        cancel_btn.setStyleSheet("""
            QPushButton {
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
                background-color: #f0f0f0;
                border: 2px solid #5C4033;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
    
    def create_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        return label
    
    def get_readonly_input_style(self):
        return """
            QLineEdit {
                color: #666666;
                font-size: 16px;
                padding: 10px;
                background-color: #f5f5f5;
                border: 2px solid #dbcfc1;
                border-radius: 10px;
            }
        """
    
    def get_editable_input_style(self):
        return """
            QLineEdit {
                color: #5C4033;
                font-size: 16px;
                padding: 10px;
                background-color: white;
                border: 2px solid #dbcfc1;
                border-radius: 10px;
            }
            QLineEdit:focus {
                border-color: #5C4033;
            }
        """
    
    def save_changes(self):
        print(f"🔄 Save changes requested for book: {self.book_data.get('title')}")
        
        # Validate copies input
        copies_text = self.copies_input.text().strip()
        if not copies_text.isdigit() or int(copies_text) < 1:
            QMessageBox.warning(self, "Validation Error", "Copies must be a positive integer")
            print(f"❌ Validation failed: Invalid copies value '{copies_text}'")
            return
        
        # Validate shelf format
        shelf = self.shelf_input.currentText().strip()  # Changed from self.shelf_input.text()
        if not re.match(r'^[A-Z][0-9]{1,5}$', shelf):
            QMessageBox.warning(self, "Validation Error", "Shelf number must be one letter (A-Z) followed by 1 to 5 digits. (e.g. A1, B12, C345)")
            print(f"❌ Validation failed: Invalid shelf format '{shelf}'")
            return
        
        print(f"✅ Validation passed - Copies: {copies_text}, Shelf: {shelf}")
        print(f"✅ Validation passed - Copies: {copies_text}, Shelf: {shelf}")
            
        try:
            print(f"📝 Starting update process...")
            
            # Update book data in memory
            old_copies = self.book_data.get('copies', 0) 
            old_available = self.book_data.get('available_copies', 0) #
            new_copies = int(copies_text)
            
            # Calculate new available copies (maintain the difference)
            copies_difference = new_copies - old_copies
            new_available_copies = max(0, old_available + copies_difference)
            
            print(f"📊 Copies calculation:")
            print(f"   Old: {old_copies} total, {old_available} available")
            print(f"   New: {new_copies} total, {new_available_copies} available")
            
            # Get current description from UI
            new_description = self.description_input.toPlainText().strip()
            
            # Update book data in memory
            self.book_data['copies'] = new_copies
            self.book_data['available_copies'] = new_available_copies
            self.book_data['shelf'] = shelf
            self.book_data['description'] = new_description
            
            # Update in database using tryDatabase.py update_table method
            book_code = self.book_data.get('book_code')
            if not book_code:
                QMessageBox.warning(self, "Error", "Cannot update: Book code not found")
                print(f"❌ Error: Book code not found in book_data")
                return
            
            print(f"📝 Updating book with BookCode: {book_code}")
            print(f"   Title: {self.book_data.get('title')}")
            
            # Prepare updates for Book table
            book_updates = {
                'BookDescription': new_description,
                'BookShelf': shelf,
                'BookTotalCopies': new_copies,
                'BookAvailableCopies': new_available_copies
            }
            
            print(f"📋 Updates to apply: {book_updates}")
            
            # Update the Book table
            print(f"🔄 Executing database update...")
            try:
                update_success = self.db_seeder.update_table("Book", book_updates, "BookCode", book_code)
                print(f"📊 Update result: {update_success} (type: {type(update_success)})")
                
                if update_success is False:
                    QMessageBox.warning(self, "Error", "Failed to update book in database. Please try again.")
                    print(f"❌ Database update returned False")
                    return
                elif update_success is None:
                    print(f"⚠️ Warning: Database update returned None, but proceeding...")
                else:
                    print(f"✅ Database update completed successfully!")
            except Exception as update_error:
                QMessageBox.warning(self, "Error", f"Database update failed: {str(update_error)}")
                print(f"❌ Database update exception: {update_error}")
                return
            
            # Verify the update worked by checking the database
            updated_books = self.db_seeder.get_all_records("Book", self.parent_window.librarian_id if hasattr(self.parent_window, 'librarian_id') else 1)
            updated_book = next((b for b in updated_books if b.get('BookCode') == book_code), None)
            
            if updated_book:
                print(f"✅ Verification successful:")
                print(f"   Description: {updated_book.get('BookDescription')}")
                print(f"   Shelf: {updated_book.get('BookShelf')}")
                print(f"   Total Copies: {updated_book.get('BookTotalCopies')}")
                print(f"   Available Copies: {updated_book.get('BookAvailableCopies')}")
            else:
                print(f"⚠️ Warning: Could not verify update in database")
            
            # Show success message
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText(f"Book '{self.book_data['title']}' has been updated successfully!\n\nUpdated fields:\n• Description: {new_description[:50]}{'...' if len(new_description) > 50 else ''}\n• Shelf: {shelf}\n• Total Copies: {new_copies}\n• Available Copies: {new_available_copies}")
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            
            print(f"🔄 Refreshing parent window display...")
            # Refresh the parent window display
            if hasattr(self.parent_window, 'load_books_from_database'):
                self.parent_window.load_books_from_database()
                print(f"✅ Books data reloaded from database")
            else:
                print(f"⚠️ Warning: parent_window doesn't have load_books_from_database method")
                
            if hasattr(self.parent_window, 'show_books_view'):
                self.parent_window.show_books_view()
                print(f"✅ Books view refreshed")
            else:
                print(f"⚠️ Warning: parent_window doesn't have show_books_view method")
            
        except Exception as e:
            error_msg = f"Error updating book: {str(e)}"
            QMessageBox.warning(self, "Error", error_msg)
            print(f"❌ {error_msg}")
            import traceback
            traceback.print_exc()
              
    def delete_book(self):
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            'Confirm Deletion', 
            f"Are you sure you want to delete '{self.book_data['title']}'?\n\nThis will permanently remove the book and all related author and genre information.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                book_code = self.book_data.get('book_code')
                if not book_code:
                    QMessageBox.warning(self, "Error", "Cannot delete: Book code not found")
                    return
                
                print(f"🗑️ Deleting book with BookCode: {book_code}")
                
                # Finally delete from Book table
                self.db_seeder.delete_table("Book", "BookCode", book_code)
                
                # Show confirmation
                msg = QMessageBox()
                msg.setWindowTitle("Deleted")
                msg.setText(f"Book '{self.book_data['title']}' has been deleted successfully!")
                msg.setIcon(QMessageBox.Information)
                msg.exec()
                
                # Refresh the parent window display
                self.parent_window.load_books_from_database()
                self.parent_window.show_books_view()
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Error deleting book: {e}")
                print(f"❌ Error deleting book: {e}")
                import traceback
                traceback.print_exc()
    
    def go_back(self):
        self.parent_window.show_books_view()

class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db_seeder = DatabaseSeeder()
        # Get librarian_id from parent (CollapsibleSidebar)
        self.librarian_id = getattr(parent, 'librarian_id', None) if parent else None
        print(f"📚 AddBookDialog initialized with librarian_id: {self.librarian_id}")
        self.setWindowTitle("Add New Book")
        self.setFixedSize(500, 700)
        self.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
            }
        """)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Book Information Section
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

        section_title = QLabel("Book Information")
        section_title.setStyleSheet("""
            QLabel {
                font-size: 20px;
                padding-top: 5px;
                padding-bottom: 12px;
            }
        """)
        info_layout.addWidget(section_title)

        # Form fields
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(0, 0, 0, 0)

        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter Title")
        self.title_input.setStyleSheet("""
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
        """)

        # Author input
        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Enter Author")
        self.author_input.setStyleSheet(self.title_input.styleSheet())

        # ISBN input
        self.isbn_input = QLineEdit()
        self.isbn_input.setPlaceholderText("Enter ISBN")
        self.isbn_input.setStyleSheet(self.title_input.styleSheet())

        form_layout.addRow("Title:", self.title_input)
        form_layout.addRow("Author:", self.author_input)
        form_layout.addRow("ISBN:", self.isbn_input)
        
        info_layout.addLayout(form_layout)

        # Search button
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
        
        layout.addWidget(info_group)

        # Book Results Section - Horizontal layout with info labels
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

        # Left side - Book Cover Preview
        left_section = QWidget()
        left_layout = QVBoxLayout(left_section)
        left_layout.setContentsMargins(0, 0, 0, 0)

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

        # Right side - Book Information
        right_section = QWidget()
        right_layout = QVBoxLayout(right_section)
        right_layout.setContentsMargins(5,5,5,5)
        right_layout.setSpacing(10)

        # Info labels
        self.info_title = QLabel("Title: ")
        self.info_author = QLabel("Author: ")
        self.info_publisher = QLabel("Publisher: ")
        self.info_isbn = QLabel("ISBN: ")
        self.info_genre = QLabel("Genre: ")
        self.info_published = QLabel("Published: ")

        info_style = """
            QLabel {
                color: #5C4033;
                font-size: 14px;
                padding: 5px;
                background-color: #f9f9f9;
                border-radius: 15px;
            }
        """
        for label in [self.info_title, self.info_author, self.info_publisher,
                      self.info_isbn, self.info_genre, self.info_published]:
            label.setStyleSheet(info_style)
            label.setWordWrap(True)
            right_layout.addWidget(label)
        right_layout.addStretch()

        results_layout.addWidget(left_section)
        results_layout.addWidget(right_section)

        layout.addWidget(results_group)

        # Bottom buttons
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(15)
        
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
        
        button_layout.addWidget(add_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addWidget(button_container)
    
    def validate_isbn(self, isbn):
        isbn_clean = re.sub(r'[^0-9X]', '', isbn.upper())

        if len(isbn_clean) not in [10, 13]:
            return False
        if len(isbn_clean) == 10:            return self.validate_isbn10(isbn_clean)
        return self.validate_isbn13(isbn_clean)
    
    def validate_isbn10(self, isbn):
        if len(isbn)!= 10:
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
    
    def validate_isbn13(self, isbn):
        if len(isbn) != 13:
            return False
        if not isbn.isdigit():
            return False 
        total = 0 
        for i in range(12):
            if i % 2 == 0:
                total += int(isbn[i])
            else:
                total += int(isbn[i]) *3
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(isbn[12])
    
    def reset_cover_preview(self):
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
        # Reset info labels
        self.info_title.setText("Title: ")
        self.info_author.setText("Author: ")
        self.info_publisher.setText("Publisher: ")
        self.info_isbn.setText("ISBN: ")
        self.info_genre.setText("Genre: ")
        self.info_published.setText("Published: ")
       
    def search_book(self): #search book through API 
        title = self.title_input.text().strip() #get user input
        author = self.author_input.text().strip()
        isbn = re.sub(r'[^0-9X]', '', self.isbn_input.text().strip().upper())  # Clean ISBN early

        #ensure all fields are filleds
        if not title or not author or not isbn:
            QMessageBox.information(self, "Search Error", "Please fill all required fields: Title, Author, and ISBN")
            return
        
        # Check for duplicate book in database
        if not self.db_seeder.handleDuplication(tableName="Book", librarianID= self.librarian_id, column="ISBN", value=isbn):
            QMessageBox.information(self, "Duplicate Book", "This book already exists in the database.")
            return

        # Validate ISBN 
        if isbn and not self.validate_isbn(isbn):
            QMessageBox.warning(self,"Invalid ISBN","The provided ISBN is invalid. Please correct the ISBN"
            )
            self.found_book_data = None
            self.reset_cover_preview() 
            return
        try:
            self.reset_cover_preview() #clear preview book preview
            API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY')
            print("ENV API:", load_dotenv())
            search_term = [f"isbn:{isbn}", f"{title}", f"{author}"] #builds search query from inputs
            query = " ".join(search_term) 
            url = f"https://www.googleapis.com/books/v1/volumes?q={query}&key={API_KEY}"
            print(f"API query: {url}")
            response = requests.get(url, timeout=10) #send requests to api
            response.raise_for_status() #raise error for bad responses
            data = response.json()

            # Check for results
            if 'items' not in data or len(data['items']) == 0:
                self.open_manual_entry(title, author, isbn) #redirect to manual entry if no match
                return

            # Process first result
            book_info = data['items'][0]['volumeInfo'] #use first book result from response 
            api_isbns = [ #extract isbn (both 10 and 13)  from the result
                re.sub(r'[^0-9X]', '', identifier['identifier'].upper())
                for identifier in book_info.get('industryIdentifiers', [])
                if identifier['type'] in ['ISBN_10', 'ISBN_13']
            ]
            print(f"Input ISBN: {isbn}, API ISBNs: {api_isbns}")

            found_isbn =isbn if (isbn and self.validate_isbn(isbn)) else api_isbns[0] if api_isbns else ''
            #stroe book data from api
            self.found_book_data = {
                'title': book_info.get('title', 'Unknown Title'),
                'author': ', '.join(book_info.get('authors', ['Unknown Author'])),
                'isbn': found_isbn,
                'publisher': book_info.get('publisher', 'Unknown Publisher'),
                'description': book_info.get('description', ''),
                'categories': book_info.get('categories', ['']),
                'image_url': book_info.get('imageLinks', {}).get('thumbnail', '').replace('http:', 'https:'),
                'published_date': book_info.get('publishedDate', ''),
                'api_isbns': api_isbns
            }
            # Update UI
            self.info_title.setText(f"Title: {self.found_book_data['title']}")
            self.info_author.setText(f"Author: {self.found_book_data['author']}")
            self.info_publisher.setText(f"Publisher: {self.found_book_data['publisher']}")
            self.info_isbn.setText(f"ISBN: {self.found_book_data['isbn'] or 'N/A'}")
            self.info_genre.setText(f"Genre: {', '.join(self.found_book_data['categories'])}")
            self.info_published.setText(f"Published: {self.found_book_data['published_date']}")
            if 'imageLinks' in book_info: #load book cover if available
                self.load_cover(self.found_book_data['image_url']) 
        except requests.exceptions.RequestException as e: # error handling
            QMessageBox.warning(self, "Network Error", "Unable to search books. Please check your internet connection")
            print(f"Network error: {e}")
            self.found_book_data = None
            self.reset_cover_preview()
        except requests.exceptions.HTTPError as e:  #for debug in request format or api key
            if response.status_code == 403:
                QMessageBox.warning(self, "API Error", "Invalid API key")
            else:
                QMessageBox.warning(self, "API Error", f"HTTP Error: {e}")
            print(f"API Error: {e}")
            self.reset_cover_preview()
        except Exception as e: #for unexpected error
            QMessageBox.warning(self, "Search Error", f"Error: {e}")
            print(f"Search error: {e}")
            self.open_manual_entry(title, author, isbn)
            self.reset_cover_preview()

    def open_manual_entry(self, title, author, isbn): #manual entry if no book is found
        print(f"📝 Opening manual entry with LibrarianID: {self.librarian_id}")
        book_data = {
            'title': title,
            'author': author if author else "Unknown Author",
            'isbn': isbn if isbn and self.validate_isbn(isbn) else '',
            'publisher': '',
            'description': '',
            'categories': [''],
            'image_url': '',
            'published_date': '',
            'image': ''
        }

        self.accept()  # Close the current dialog

        details_dialog = BookDetailsDialog(
            parent = self.parent,
            book_data = book_data,
            is_found_book = False #allow edit all fields
        )

        # Configure window to be maximizable and make it fill the screen
        details_dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.Window)
        details_dialog.resize(QApplication.primaryScreen().availableSize() * 0.9)
        details_dialog.showFullScreen()  

        close_btn = QPushButton("X", details_dialog)
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

        # Apply fullscreen stylesheet
        details_dialog.setStyleSheet("""
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
        
        # Add close button
        #screen_size = QApplication.primaryScreen().size()

        close_btn.setFixedSize(40, 40)

        dialog_width = details_dialog.width()
        close_btn.move(dialog_width -0, 20)

        close_btn.raise_()
        close_btn.clicked.connect(details_dialog.reject)
        
        # Now execute the dialog to make it modal
        result = details_dialog.exec_()
        
    
        if result == QDialog.Accepted:
            standardized_book = {
                'title': details_dialog.book_data['title'],
                'author': details_dialog.book_data['author'],
                'isbn': details_dialog.book_data['isbn'],
                'publisher': details_dialog.book_data['publisher'], 
                'genre': details_dialog.book_data['genre'],
                'description': details_dialog.book_data['description'],
                'shelf': details_dialog.book_data['shelf'],
                'copies': details_dialog.book_data['copies'],
                'image': details_dialog.book_data.get('image', ''),
                'available_copies': details_dialog.book_data['available_copies']
            }
            
            print(f"Adding book to book-data: {standardized_book}")
            self.parent.books_data.append(standardized_book)
            self.parent.refresh_books_display()
            
            # Save to database using the same logic as add_book method
            # 1. Prepare data for Book table
            book_data = {
                'BookTitle': standardized_book['title'],
                'Publisher': standardized_book.get('publisher', 'Unknown Publisher'),  
                'BookDescription': standardized_book['description'],
                'BookShelf': standardized_book['shelf'],  # Use BookShelf to match actual database
                'ISBN': standardized_book['isbn'],
                'BookTotalCopies': standardized_book['copies'],
                'BookAvailableCopies': standardized_book['available_copies'],
                'BookCover': standardized_book['image'],
                'LibrarianID': self.librarian_id  # Use the actual logged-in librarian ID
            }

            # 2. Use seed_data to insert into Book table
            book_columns = ['BookTitle', 'Publisher', 'BookDescription', 'BookShelf', 'ISBN', 
                        'BookTotalCopies', 'BookAvailableCopies', 'BookCover', 'LibrarianID']
            
            try:
                # Insert book using seed_data
                print(f"📝 Saving manual entry book with LibrarianID: {self.librarian_id}")
                self.db_seeder.seed_data(
                    tableName="Book",
                    data=[book_data],
                    columnOrder=book_columns
                )

                # 3. Get the BookCode of the inserted book
                # Query to find the book we just inserted
                conn, cursor = self.db_seeder.get_connection_and_cursor()
                try:
                    cursor.execute("""
                        SELECT BookCode FROM Book 
                        WHERE BookTitle = ? AND ISBN = ? AND BookShelf = ?
                        ORDER BY BookCode DESC LIMIT 1
                    """, (standardized_book['title'], standardized_book['isbn'], standardized_book['shelf']))
                    
                    result = cursor.fetchone()
                    if not result:
                        print("❌ Error: Could not find the inserted book")
                        return
                    
                    book_code = result[0]
                    print(f"✓ Found BookCode: {book_code}")
                finally:
                    conn.close()

                # 4. Use seed_data for BookAuthor - handle multiple authors
                authors = standardized_book['author']
                if isinstance(authors, str):
                    authors = [authors]  # Convert string to list if needed
                
                author_data_list = []
                for author in authors:
                    author_data_list.append({
                        'BookCode': book_code,
                        'bookAuthor': author.strip()
                    })
                
                if author_data_list:
                    self.db_seeder.seed_data(
                        tableName="BookAuthor",
                        data=author_data_list,
                        columnOrder=['BookCode', 'bookAuthor']
                    )

                # 5. Use seed_data for Book_Genre - handle multiple genres
                genres = standardized_book['genre']
                if isinstance(genres, str):
                    genres = [genres]  # Convert string to list if needed
                
                genre_data_list = []
                for genre in genres:
                    genre_data_list.append({
                        'BookCode': book_code,
                        'Genre': genre.strip()
                    })
                
                if genre_data_list:
                    self.db_seeder.seed_data(
                        tableName="Book_Genre",
                        data=genre_data_list,
                        columnOrder=['BookCode', 'Genre']
                    )

                print(f"✓ Manual entry book with {len(author_data_list)} authors and {len(genre_data_list)} genres saved successfully with BookCode: {book_code}")
            except Exception as e:
                print(f"❌ Error saving manual entry book to database: {e}")
                import traceback
                traceback.print_exc()
            
            self.accept()
    def load_cover(self, image_url):
        try: #download image
            response = requests.get(image_url, timeout = 10)
            response.raise_for_status()

            pixmap = QPixmap() #create qpixmap from download
            pixmap.loadFromData(response.content)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled( #scale image to fit in preview
                    self.book_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.book_preview.setPixmap(scaled_pixmap)
                self.book_preview.setStyleSheet("")

                if not os.path.exists('assets'): 
                    os.makedirs('assets') #creates local folder to save image locally
                isbn = self.found_book_data.get('isbn', 'temp') #use isbn for filename, temp if not available
                image_path = os.path.normpath(os.path.join('assets', f"book_cover_{isbn}.png"))
                with open(image_path, 'wb') as f: #save iamge file
                    f.write(response.content)
                self.found_book_data['image'] = image_path #store the imagepath in book_data
                print(f"API cover saved to: {image_path}")
            else:
                self.book_preview.setText("")
                self.book_preview.setStyleSheet("""
                    QLabel {
                        background-color: #dbcfc1;
                        border-radius: 8px;
                        border: 2px solid #5C4033;
                    }
                """)
                self.found_book_data['image'] = ''
        except Exception as e:
            print(f"Failed to load API image: {e}")
            self.book_preview.setText("Cover not available")
            self.found_book_data['image'] = ''
    
    def add_book(self):
        print(f"📚 Adding book with LibrarianID: {self.librarian_id}")
        title = self.title_input.text().strip()
        author = self.author_input.text().strip()
        isbn = re.sub(r'[^0-9X]', '', self.isbn_input.text().strip().upper())

        if not title or not author or not isbn:
            QMessageBox.information(self, "Adding book Error", "Please fill in all required fields: Title, Author, and ISBN")
            return
        if isbn and not self.validate_isbn(isbn):
            QMessageBox.warning(self, "Validation Error", "Invalid ISBN")
            return

        book_data = self.found_book_data or {
            'title': title,
            'author': author if author else 'Unknown Author',
            'isbn': isbn if isbn and self.validate_isbn(isbn) else '',
            'publisher': '',
            'description': '',
            'categories': [''],
            'image_url': '',
            'published_date': '',
            'image': ''
        }
        
        # Close current dialog first
        self.accept()
        
        details_dialog = BookDetailsDialog(
            parent=self.parent,  
            book_data=book_data,
            is_found_book=bool(self.found_book_data)
        )
        
        # Configure window to be maximizable and fullscreen
        details_dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.Window)
        details_dialog.resize(QApplication.primaryScreen().availableSize() * 0.9)
        details_dialog.showFullScreen()

        # Add close button
        close_btn = QPushButton("X", details_dialog)
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
        close_btn.setFixedSize(40, 40)
        
        dialog_width = details_dialog.width()
        close_btn.move(dialog_width - 60, 20)
        close_btn.raise_()
        close_btn.clicked.connect(details_dialog.reject)
        
        # Now execute the dialog
        result = details_dialog.exec_()
        
        # Continue with existing code for when dialog is accepted
        if result == QDialog.Accepted:
            standardized_book = {
                'title': details_dialog.book_data['title'],
                'author': details_dialog.book_data['author'],
                'isbn': details_dialog.book_data['isbn'],
                'publisher': details_dialog.book_data['publisher'], 
                'genre': details_dialog.book_data['genre'],
                'description': details_dialog.book_data['description'],
                'shelf': details_dialog.book_data['shelf'],
                'copies': details_dialog.book_data['copies'],
                'image': details_dialog.book_data.get('image', ''),
                'available_copies': details_dialog.book_data['available_copies']
            }
            
            print(f"Adding book to books_data: {standardized_book}")
            self.parent.books_data.append(standardized_book)
            self.parent.refresh_books_display()
            
            # 1. Prepare data for Book table
            book_data = {
                'BookTitle': standardized_book['title'],
                'Publisher': standardized_book.get('publisher', 'Unknown Publisher'), 
                'BookDescription': standardized_book['description'],
                'BookShelf': standardized_book['shelf'],  # Use BookShelf to match database
                'ISBN': standardized_book['isbn'],
                'BookTotalCopies': standardized_book['copies'],
                'BookAvailableCopies': standardized_book['available_copies'],
                'BookCover': standardized_book['image'],
                'LibrarianID': self.librarian_id  # Use the actual logged-in librarian ID
            }

            # 2. Use seed_data to insert into Book table
            book_columns = ['BookTitle', 'Publisher','BookDescription', 'BookShelf', 'ISBN', 
                        'BookTotalCopies', 'BookAvailableCopies', 'BookCover', 'LibrarianID']
            
            try:
                # Insert book using seed_data
                print(f"📚 Saving API book with LibrarianID: {self.librarian_id}")
                self.db_seeder.seed_data(
                    tableName="Book",
                    data=[book_data],
                    columnOrder=book_columns
                )

                # 3. Get the BookCode of the inserted book
                # Query to find the book we just inserted
                conn, cursor = self.db_seeder.get_connection_and_cursor()
                try:
                    cursor.execute("""
                        SELECT BookCode FROM Book 
                        WHERE BookTitle = ? AND ISBN = ? AND BookShelf = ?
                        ORDER BY BookCode DESC LIMIT 1
                    """, (standardized_book['title'], standardized_book['isbn'], standardized_book['shelf']))
                    
                    result = cursor.fetchone()
                    if not result:
                        print("❌ Error: Could not find the inserted book")
                        return
                    
                    book_code = result[0]
                    print(f"✓ Found BookCode: {book_code}")
                finally:
                    conn.close()

                # 4. Use seed_data for BookAuthor - handle multiple authors
                authors = standardized_book['author']
                if isinstance(authors, str):
                    authors = [authors]  # Convert string to list if needed
                
                author_data_list = []
                for author in authors:
                    author_data_list.append({
                        'BookCode': book_code,
                        'bookAuthor': author.strip()
                    })
                
                if author_data_list:
                    self.db_seeder.seed_data(
                        tableName="BookAuthor",
                        data=author_data_list,
                        columnOrder=['BookCode', 'bookAuthor']
                    )

                # 5. Use seed_data for Book_Genre - handle multiple genres
                genres = standardized_book['genre']
                if isinstance(genres, str):
                    genres = [genres]  # Convert string to list if needed
                
                genre_data_list = []
                for genre in genres:
                    genre_data_list.append({
                        'BookCode': book_code,
                        'Genre': genre.strip()
                    })
                
                if genre_data_list:
                    self.db_seeder.seed_data(
                        tableName="Book_Genre",
                        data=genre_data_list,
                        columnOrder=['BookCode', 'Genre']
                    )

                print(f"✓ Book with {len(author_data_list)} authors and {len(genre_data_list)} genres saved successfully with BookCode: {book_code}")
            except Exception as e:
                print(f"❌ Error saving book to database: {e}")
                import traceback
                traceback.print_exc()

class BookDetailsDialog(QDialog):
    def __init__(self, parent=None, book_data=None, is_found_book=False):
        super().__init__(parent)
        self.parent = parent
        self.book_data = book_data or {}
        self.is_found_book = is_found_book
        self.image_preview_size = QSize(180, 210)
        self.setup_ui()
        self.populate_fields()

    def setup_ui(self):
        self.setWindowTitle("Book Details")
        # Remove fixed size to allow fullscreen
        # self.setFixedSize(600, 700)
        self.setStyleSheet('''
            QDialog {
                background-color: #f1efe3;
                font-size: 14px;
            }
        ''')
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 50, 30, 30)
        main_layout.setSpacing(20)

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
                width: 15px;
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
        
        # Create container widget for scroll area
        content_widget = QWidget()
        content_widget.setMinimumWidth(800)  # Ensure content is wide enough
        content_widget.setStyleSheet("background-color: #f1efe3;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(30, 40, 30, 30)
        content_layout.setSpacing(25)  

        # Add title
        title_label = QLabel("Enter Book Details")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: #5C4033;
                margin-bottom: 10px;
                background: transparent;
            }
        """)
        content_layout.addWidget(title_label)

        # =============== BOOK INFORMATION (FULL WIDTH TOP) ===============
        info_group = QGroupBox("Book Information")
        info_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #dbcfc1;
                color: #5C4033;
                font-size: 25px;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left:8px;
                padding: 0 3px;
            }
        """)
        
        info_layout = QFormLayout(info_group)
        info_layout.setContentsMargins(15, 25, 15, 25)  
        info_layout.setVerticalSpacing(20)  
        info_layout.setHorizontalSpacing(15)
        
        # Input style
        input_style = """
            QLineEdit, QTextEdit, QSpinBox, QComboBox {
                background-color: white;
                border: 1px solid #dbcfc1;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                color: #5C4033;
                
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #5C4033;
            }
            QLineEdit[readOnly="true"], QTextEdit[readOnly="true"] {
                background-color: #f5f5f5;
                color: #666666;
            }
            QLineEdit::placeholder, QTextEdit::placeholder {
                color: #999999;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 16px;
                background-color: #f5f5f5;
                border: none;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #e0e0e0;
            }
            QTextEdit {
                min-height: 30px;  
            }
        """
        
        # Label style
        label_style = """
            QLabel {
                color: #5C4033;
                font-size: 14px;
                font-weight: bold;
                background-color: #f9f9f9;
                border: 1px solid #dbcfc1;
                border-radius: 8px;
                padding: 8px 12px;
                margin-right: 10px;
            }
        """
        
        # Form fields
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter Title")
        self.title_edit.setStyleSheet(input_style)
        self.title_edit.setFixedHeight(35)  
        
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Enter Author")
        self.author_edit.setStyleSheet(input_style)
        self.author_edit.setFixedHeight(35)
        
        self.isbn_edit = QLineEdit()
        self.isbn_edit.setPlaceholderText("Enter ISBN")
        self.isbn_edit.setStyleSheet(input_style)
        self.isbn_edit.setFixedHeight(35)
        
        self.publisher_edit = QLineEdit()
        self.publisher_edit.setPlaceholderText("Enter Publisher")
        self.publisher_edit.setStyleSheet(input_style)
        self.publisher_edit.setFixedHeight(35)
        
        # Genres container
        self.genre_container = QWidget()
        genre_container_layout = QVBoxLayout(self.genre_container)
        genre_container_layout.setContentsMargins(0, 0, 0, 0)
        genre_container_layout.setSpacing(10)  # More space between elements

        # Genre help text
        genre_help = QLabel("Select a genre or type a new one, then press Enter to add it")
        genre_help.setStyleSheet("""
            QLabel {
                color: #777777;
                font-size: 12px;
                font-style: italic;
                background: transparent;
                border: none;
            }
        """)
        genre_container_layout.addWidget(genre_help)

        # Container for selected genre tags
        self.selected_genres_container = QWidget()
        self.selected_genres_layout = QHBoxLayout(self.selected_genres_container)
        self.selected_genres_layout.setContentsMargins(0, 0, 0, 0)
        self.selected_genres_layout.setSpacing(5)
        self.selected_genres_layout.setAlignment(Qt.AlignLeft)

        # Genre combo box
        self.genre_combo = QComboBox()
        self.genre_combo.setStyleSheet(input_style)
        self.genre_combo.setFixedHeight(55)
        self.genre_combo.setEditable(True)
        self.genre_combo.setInsertPolicy(QComboBox.NoInsert)
        self.genre_combo.setPlaceholderText("Select or type a genre")

        # Add popular genres as options
        common_genres = [
            "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", "Mystery", 
            "Thriller", "Romance", "Historical Fiction", "Biography", "Autobiography",
            "Self-Help", "Business", "Children's", "Young Adult", "Poetry", 
            "Science", "History", "Philosophy", "Religion", "Art", "Cooking"
        ]
        self.genre_combo.addItems(sorted(common_genres))

        # Connect signals
        self.genre_combo.currentIndexChanged.connect(self.add_current_genre_from_dropdown)
        self.genre_combo.lineEdit().returnPressed.connect(self.add_current_genre)

        genre_container_layout.addWidget(self.genre_combo)
        genre_container_layout.addWidget(self.selected_genres_container)

        # Initialize selected genres list
        self.selected_genres = []
        
        # Description text area
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter Description")
        self.description_edit.setStyleSheet(input_style)
        self.description_edit.setMinimumHeight(45)

        # Labels
        title_label = QLabel("Title:")
        title_label.setStyleSheet(label_style)
        author_label = QLabel("Author:")
        author_label.setStyleSheet(label_style)
        isbn_label = QLabel("ISBN:")
        isbn_label.setStyleSheet(label_style)
        publisher_label = QLabel("Publisher:")
        publisher_label.setStyleSheet(label_style)
        genre_label = QLabel("Genre:")
        genre_label.setStyleSheet(label_style)
        description_label = QLabel("Description:")
        description_label.setStyleSheet(label_style)

        # Add fields to form with styled labels
        info_layout.addRow(title_label, self.title_edit)
        info_layout.addRow(author_label, self.author_edit)
        info_layout.addRow(isbn_label, self.isbn_edit)
        info_layout.addRow(publisher_label, self.publisher_edit)
        info_layout.addRow(genre_label, self.genre_container)
        info_layout.addRow(description_label, self.description_edit)

        # Add Book Information group to content layout
        content_layout.addWidget(info_group)

        # =============== HORIZONTAL LAYOUT FOR LIBRARY INFO AND BOOK COVER ===============
        lib_cover_container = QWidget()
        lib_cover_layout = QHBoxLayout(lib_cover_container)
        lib_cover_layout.setContentsMargins(0, 0, 0, 0)
        lib_cover_layout.setSpacing(20)
        
        # =============== LIBRARY INFORMATION (LEFT SIDE) ===============
        lib_group = QGroupBox("Library Information")
        lib_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #dbcfc1;
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0px 5px;
                background: transparent;
            }
        """)
        
        lib_layout = QFormLayout(lib_group)
        lib_layout.setContentsMargins(15, 25, 15, 25)  # Increased vertical margins
        lib_layout.setVerticalSpacing(20)  # More space between rows
        lib_layout.setHorizontalSpacing(15)

        # Library info fields - Create shelf dropdown instead of text input
        self.shelf_edit = QComboBox()
        self.shelf_edit.setEditable(False)
        self.shelf_edit.setPlaceholderText("Select Shelf")
        self.shelf_edit.setStyleSheet("""
            QComboBox {
                color: #5C4033;
                font-size: 14px;
                padding: 10px 20px;
                background-color: white;
                border: 1px solid #dbcfc1;
                border-radius: 5px;
            }
            QComboBox:focus {
                border: 1px solid #5C4033;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border: 1px solid #5C4033;
                width: 8px;
                height: 8px;
                background-color: #5C4033;
            }
            QComboBox[readOnly="true"] {
                background-color: #f5f5f5;
                color: #666666;
            }
        """)
        self.shelf_edit.setFixedHeight(35)  # Taller input fields

        # Populate shelf dropdown with available shelves from database
        try:
            from tryDatabase import DatabaseSeeder
            db_seeder = DatabaseSeeder()
            # Get librarian_id from parent
            librarian_id = getattr(self.parent, 'librarian_id', 1)
            shelf_records = db_seeder.get_all_records("BookShelf", librarian_id)
            available_shelves = [record['ShelfId'] for record in shelf_records if record.get('ShelfId')]
            
            print(f"📚 BookDetailsDialog - Available shelves from DB: {available_shelves}")
            
            # If no shelves exist for this librarian, create default shelf A1
            if not available_shelves:
                print(f"📚 BookDetailsDialog - No shelves found, creating default shelf A1")
                try:
                    db_seeder.seed_data("BookShelf", [{"ShelfId": "A1", "LibrarianID": librarian_id}], ["ShelfId", "LibrarianID"])
                    available_shelves = ["A1"]
                    print(f"📚 BookDetailsDialog - Created default shelf A1")
                except Exception as seed_error:
                    print(f"⚠️ Could not create default shelf: {seed_error}")
                    available_shelves = ["A1"]  # Use A1 anyway
            
            # Add all available shelves to dropdown
            self.shelf_edit.addItems(available_shelves)
            print(f"📚 BookDetailsDialog - Added shelves to dropdown: {available_shelves}")
                        
        except Exception as e:
            print(f"Error loading shelves in BookDetailsDialog: {e}")
            # Fallback to default shelf
            self.shelf_edit.addItem("A1")

        self.copies_spin = QSpinBox()
        self.copies_spin.setMaximum(999)
        self.copies_spin.setMinimum(1)
        self.copies_spin.setValue(1)
        self.copies_spin.setStyleSheet(input_style)
        self.copies_spin.setFixedHeight(35)

        # Library info labels
        shelf_label = QLabel("Shelf Number:")
        shelf_label.setStyleSheet(label_style)
        copies_label = QLabel("Total Copies:")
        copies_label.setStyleSheet(label_style)

        lib_layout.addRow(shelf_label, self.shelf_edit)
        lib_layout.addRow(copies_label, self.copies_spin)

        # =============== BOOK COVER (RIGHT SIDE) ===============
        image_group = QGroupBox("Book Cover")
        image_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #dbcfc1;
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background: transparent;
            }
        """)

        image_layout = QHBoxLayout(image_group)
        image_layout.setContentsMargins(15, 20, 15, 20)
        image_layout.setSpacing(15)

        image_container = QWidget()
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(0, 0, 0, 0)
        image_container_layout.setSpacing(10)

        self.image_preview = QLabel()
        self.image_preview.setFixedSize(self.image_preview_size)
        self.image_preview.setMinimumSize(80, 100)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                background-color: #f5f5f5;
                border: 2px dashed #dbcfc1;
                border-radius: 10px;
            }
        """)
        
        image_container_layout.addWidget(self.image_preview, alignment=Qt.AlignCenter)

        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: none; background: transparent;")
        image_container_layout.addWidget(self.image_label)

        image_layout.addWidget(image_container)

        self.image_btn = QPushButton("Upload Cover")
        self.image_btn.clicked.connect(self.upload_image)
        self.image_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C4033;
                color: white;
                padding: 12px 20px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        self.image_btn.setFixedHeight(45)
        image_layout.addWidget(self.image_btn, alignment=Qt.AlignCenter)

        # Load cover preview if needed
        if self.is_found_book and self.book_data.get('image'):
            self.load_cover_preview()

        # =============== ADD BOTH GROUPS TO HORIZONTAL LAYOUT ===============
        # Library Info on the left (60% width), Book Cover on the right (40% width)
        lib_cover_layout.addWidget(lib_group, 6)   # 60% width
        lib_cover_layout.addWidget(image_group, 4)  # 40% width

        # Add the horizontal container to content layout
        content_layout.addWidget(lib_cover_container)

        # =============== BUTTONS ===============
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_btn = QPushButton("Save Book")
        save_btn.clicked.connect(self.save_book)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C4033;
                color: white;
                padding: 14px 20px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #5C4033;
                padding: 14px 20px;
                border: 2px solid #5C4033;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)

        button_layout.addStretch(1)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)

        # Set content widget as scroll area's widget
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

        # Set readOnly properties based on is_found_book
        if self.is_found_book:
            self.title_edit.setReadOnly(True)
            self.author_edit.setReadOnly(True)
            self.isbn_edit.setReadOnly(True)
            self.publisher_edit.setReadOnly(True)
            if self.book_data.get('categories', ['N/A'])[0] != 'N/A':
                self.genre_combo.setEnabled(False)
        else:
            self.title_edit.setReadOnly(False)
            self.author_edit.setReadOnly(False)
            self.isbn_edit.setReadOnly(False)
            self.publisher_edit.setReadOnly(False)
            self.genre_combo.setEnabled(True)

    def load_cover_preview(self):
        try:
            image_path = os.path.normpath(self.book_data['image'])
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    self.image_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_preview.setScaledContents(True)
                self.image_label.setText(f"Image: {os.path.basename(image_path)}")
            else:
                self.image_preview.setText("")
                self.image_preview.setStyleSheet("""
                    QLabel {
                        background-color: #dbcfc1;
                        border-radius: 8px;
                        border: 2px solid #5C4033;
                    }
                """)
                self.image_label.setText("No image selected")
        except Exception as e:
            print(f"Error loading local image {image_path}: {e}")
            self.image_preview.setText("")
            self.image_preview.setStyleSheet("""
                QLabel {
                    background-color: #dbcfc1;
                    border-radius: 8px;
                    border: 2px solid #5C4033;
                }
            """)
            self.image_label.setText("No image selected")

    def populate_fields(self):
        self.title_edit.setText(self.book_data.get('title', ''))
        author = self.book_data.get('author', '')
        if isinstance(author, list):
            author = ', '.join(author)
        self.author_edit.setText(author)
        self.isbn_edit.setText(self.book_data.get('isbn', ''))
        self.publisher_edit.setText(self.book_data.get('publisher', ''))
        genres = self.book_data.get('categories', [''])
        if not isinstance(genres, list):
            genres = [genres]
        
        self.selected_genres = [g.strip() for g in genres if g.strip()]
        self.update_genre_tags()
        self.description_edit.setText(self.book_data.get('description', ''))
        
        # Set shelf value in combo box
        shelf = self.book_data.get('shelf', '')
        if shelf:
            index = self.shelf_edit.findText(shelf)
            if index >= 0:
                self.shelf_edit.setCurrentIndex(index)
            else:
                # If shelf is not in the list, add it and select it
                self.shelf_edit.addItem(shelf)
                self.shelf_edit.setCurrentText(shelf)

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Book Cover", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            try:
                if not os.path.exists('assets'):
                    os.makedirs('assets')
                isbn = re.sub(r'[^0-9X]', '', self.isbn_edit.text().strip().upper()) or 'temp'
                filename = f"book_cover_{isbn}.png"
                image_path = os.path.normpath(os.path.join('assets', filename))
                shutil.copy(file_path, image_path)
                print(f"Image copied to: {image_path}, Exists: {os.path.exists(image_path)}")
                if os.path.exists(image_path):
                    self.book_data['image'] = image_path
                    self.image_label.setText(f"Image: {os.path.basename(image_path)}")
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            self.image_preview.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.image_preview.setPixmap(scaled_pixmap)
                        self.image_preview.setStyleSheet("")
                    else:
                        print(f"Invalid image file: {image_path}")
                        self.image_preview.setText("")
                        self.image_preview.setStyleSheet("""
                            QLabel {
                                background-color: #dbcfc1;
                                border-radius: 8px;
                                border: 2px solid #5C4033;
                            }
                        """)
                        self.image_label.setText("Invalid image")
                else:
                    print(f"Failed to copy image to: {image_path}")
                    self.image_preview.setText("")
                    self.image_preview.setStyleSheet("""
                        QLabel {
                            background-color: #dbcfc1;
                            border-radius: 8px;
                            border: 2px solid #5C4033;
                        }
                    """)
                    self.image_label.setText("Image copy failed")
            except Exception as e:
                print(f"Error uploading image: {e}")
                self.image_preview.setText("")
                self.image_preview.setStyleSheet("""
                    QLabel {
                        background-color: #dbcfc1;
                        border-radius: 8px;
                        border: 2px solid #5C4033;
                    }
                """)
                self.image_label.setText("Image upload failed")
 
    def save_book(self):
        fields = [
            ('Title', lambda: self.title_edit.text().strip(), "Title is required", None),
            ('Author', lambda: self.author_edit.text().strip(), "Author is required", None),
            ('ISBN', lambda: self.isbn_edit.text().strip(), "ISBN is required", None),
            ('Publisher', lambda: self.publisher_edit.text().strip(), "Publisher is required", None),
            ('Description', lambda: self.description_edit.toPlainText().strip(), "Description is required", None),
            ('Shelf Number', lambda: self.shelf_edit.currentText().strip(), "Shelf number is required", None),
        ]
        
        isbn = re.sub(r'[^0-9X]', '', self.isbn_edit.text().strip().upper())
        
        # Internal ISBN validation instead of using parent.validate_isbn
        is_valid_isbn = False
        if len(isbn) == 10:
            # ISBN-10 validation
            try:
                total = 0
                for i in range(9):
                    if not isbn[i].isdigit():
                        break
                    total += int(isbn[i]) * (10 - i)
                check = 11 - (total % 11)
                if check == 11:
                    check = '0'
                elif check == 10:
                    check = 'X'
                else:
                    check = str(check)
                is_valid_isbn = (isbn[9] == check)
            except:
                is_valid_isbn = False
        elif len(isbn) == 13:
            # ISBN-13 validation
            try:
                if not isbn.isdigit():
                    is_valid_isbn = False
                else:
                    total = 0
                    for i in range(12):
                        if i % 2 == 0:
                            total += int(isbn[i])
                        else:
                            total += int(isbn[i]) * 3
                    check = (10 - (total % 10)) % 10
                    is_valid_isbn = (int(isbn[12]) == check)
            except:
                is_valid_isbn = False
        
        if isbn and not is_valid_isbn:
            QMessageBox.warning(self, "Validation Error", "Invalid ISBN")
            return
        
        # Check for duplicate book in database
        if not self.db_seeder.handleDuplication(tableName="Book", librarianID= self.librarian_id, column="ISBN", value=isbn):
            QMessageBox.information(self, "Duplicate Book", "This book already exists in the database.")
            return
        
        shelf = self.shelf_edit.currentText().strip()
        if not re.match(r'^[A-Z][0-9]{1,5}$', shelf):
            QMessageBox.warning(self, "Validation Error", "Shelf number must be one letter (A-Z) followed by 1 to 5 digits. (e.g. A1, B12, C345)")
            return
            
        for field_name, getter, error_msg, validator in fields:
            value = getter()
            if not value or (validator and not validator(value)):
                QMessageBox.warning(self, "Validation Error", error_msg)
                return
                
        authors = list(set([a.strip() for a in self.author_edit.text().strip().split(',') if a.strip()]))
        genres = list(set(self.selected_genres)) 
        
        if not genres:
            QMessageBox.warning(self, "Validation Error", "At least one(1) genre is required")
            return

        try:
            # Update book_data with form values
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
            
            print(f"Saving book: {self.book_data}")
            QMessageBox.information(self, "Success", f"Book '{self.book_data['title']}' has been added to the library")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unexpected Error: {e}")
            print(f"Unexpected Error: {e}")
            
    def handle_genre_input(self, text):
        """Handle genre input changes"""
        if not text.strip():
            return

    def add_current_genre(self):
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
        tag.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #dbcfc1;
                border-radius: 10px;
            }
        """)
        tag_layout = QHBoxLayout(tag)
        tag_layout.setContentsMargins(8, 2, 8, 2)
        tag_layout.setSpacing(5)
        
        label = QLabel(genre)
        label.setStyleSheet("background: transparent; border: none;")
        
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(16, 16)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #5C4033;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                color: red;
            }
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
    
    def add_current_genre_from_dropdown(self, index):
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
            self.add_current_genre()
            # Stop event propagation
            event.accept()
        else:
            # For all other keys, pass to parent handler
            super().keyPressEvent(event)
            
#MAIN WINDOW
class CollapsibleSidebar(QWidget):
    def __init__(self, librarian_id=None):
        super().__init__()
        self.librarian_id = librarian_id
        self.db_seeder = DatabaseSeeder()
        self.setWindowTitle("Library Management System")
        self.showMaximized()
        
        #ASK: TATANGGALIN KO NA BA TO GUYS?
        # Initialize books data PYTHON LIST!
        self.books_data = []
        self.original_books_data = []
        
        # Main content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f1efe3;")
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main books view
        self.main_books_view = self.create_main_books_view()
        self.content_layout.addWidget(self.main_books_view)
        
        self.current_shelf = None
        # Keep track of current view
        self.current_view = "books"
        self.sidebar = NavigationSidebar()
        self.sidebar.on_navigation_clicked = nav_manager.handle_navigation

        # Load initial data from database
        self.load_books_from_database()
        
        # Combine sidebar and content area
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)

    def load_books_from_database(self):
        """Load books data from database seeder"""
        try:
            print("Loading books from database...")
            
            # Get data from all three tables, passing librarian_id for filtering
            books = self.db_seeder.get_all_records("Book", self.librarian_id or 1)
            book_authors = self.db_seeder.get_all_records("BookAuthor", self.librarian_id or 1)
            book_genres = self.db_seeder.get_all_records("Book_Genre", self.librarian_id or 1)
            book_shelf = self.db_seeder.get_all_records("BookShelf", self.librarian_id or 1)
            
            print(f"Found {len(books)} books, {len(book_authors)} authors, {len(book_genres)} genres")
            
            # Debug: Print first few records to understand structure
            if books:
                print("Sample book record:", books[0])
            if book_authors:
                print("Sample author record:", book_authors[0])
            if book_genres:
                print("Sample genre record:", book_genres[0])
            
            # Clear existing data
            self.books_data = []
            
            # Process each book
            for book in books:
                try:
                    book_code = book.get("BookCode")
                    if not book_code:
                        print(f"Warning: Book missing BookCode: {book}")
                        continue
                    
                    # Find all authors for this book
                    book_authors_list = [
                        author["bookAuthor"] for author in book_authors 
                        if author.get("BookCode") == book_code and author.get("bookAuthor")
                    ]
                    
                    # Find all genres for this book
                    book_genres_list = [
                        genre["Genre"] for genre in book_genres 
                        if genre.get("BookCode") == book_code and genre.get("Genre")
                    ]
                    
                    # Use "Unknown" if no authors/genres found
                    if not book_authors_list:
                        book_authors_list = ["Unknown Author"]
                    if not book_genres_list:
                        book_genres_list = ["Unknown Genre"]
                    
                    # Create book data dictionary
                    book_data = {
                        "book_code": book_code,
                        "title": book.get("BookTitle", "Unknown Title"),
                        "author": book_authors_list,  # Keep as list for multiple authors
                        "genre": book_genres_list,    # Keep as list for multiple genres
                        "isbn": book.get("ISBN", ""),
                        "publisher": book.get("Publisher", "Unknown Publisher"), 
                        "description": book.get("BookDescription", ""),
                        "shelf": book.get("BookShelf", ""),  # Changed from BookShelf to BookShelf
                        "copies": book.get("BookTotalCopies", 0),
                        "available_copies": book.get("BookAvailableCopies", 0),
                        "image": book.get("BookCover", "")
                    }
                    
                    self.books_data.append(book_data)
                    print(f"Processed book: {book_data['title']} by {book_data['author']}")
                    
                except Exception as e:
                    print(f"Error processing book {book}: {e}")
                    continue
            
            # Store original data for search functionality
            self.original_books_data = self.books_data.copy()
            
            print(f"Successfully loaded {len(self.books_data)} books")
            
            # Populate the display
            if hasattr(self, 'grid_layout'):
                self.populate_books()
                
        except Exception as e:
            print(f"Error loading books from database: {e}")
            import traceback
            traceback.print_exc()
            # Initialize with empty data if there's an error
            self.books_data = []
            self.original_books_data = []
    
    #SORTING BOOKS 
    def show_sort_options(self):
        """Show a popup menu with sorting options"""
        # Create menu
        sort_menu = QMenu(self)
        sort_menu.setStyleSheet("""
            QMenu {
                background-color: #FFFEF0;
                border: 2px solid #5C4033;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #5C4033;
                font-size: 14px;
            }
            QMenu::item:selected {
                background-color: #dbcfc1;
                border-radius: 4px;
            }
        """)
        
        # Add sort options
        sort_menu.addAction("Title (A-Z)", lambda: self.sort_books("title", True))
        sort_menu.addAction("Title (Z-A)", lambda: self.sort_books("title", False))
        sort_menu.addAction("Author (A-Z)", lambda: self.sort_books("author", True))
        sort_menu.addAction("Author (Z-A)", lambda: self.sort_books("author", False))
        sort_menu.addAction("Most Copies", lambda: self.sort_books("copies", False))
        sort_menu.addAction("Least Copies", lambda: self.sort_books("copies", True))
        
        # Show menu at button position
        sort_menu.exec(self.sort_button.mapToGlobal(self.sort_button.rect().bottomLeft()))

    def sort_books(self, key, ascending=True):
        """Sort books by the given key using database sorting"""
        try:
            # Map the sorting parameters to the database filter names
            filter_map = {
                ("title", True): "ascendingTitle",
                ("title", False): "descendingTitle", 
                ("author", True): "ascendingAuthor",
                ("author", False): "descendingAuthor",
                ("copies", False): "mostCopies",  # Most copies = descending
                ("copies", True): "leastCopies"   # Least copies = ascending
            }
            
            filter_name = filter_map.get((key, ascending))
            if not filter_name:
                print(f"Unknown sort key: {key}, ascending: {ascending}")
                return
            
            print(f"Sorting books by {filter_name} for librarian {self.librarian_id}")
            
            # Get sorted books from database
            sorted_books = self.db_seeder.filterBooks(filter_name, self.librarian_id or 1)
            
            if not sorted_books:
                print("No books returned from database sort")
                # Show message to user if no books found
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Sort Books",   
                    "No books found to sort."
                )
                return
            
            # Get the authors and genres for the sorted books
            book_authors = self.db_seeder.get_all_records("BookAuthor", self.librarian_id or 1)
            book_genres = self.db_seeder.get_all_records("Book_Genre", self.librarian_id or 1)
            books_shelf = self.db_seeder.get_all_records("BookShelf", self.librarian_id or 1)
            
            # Process the sorted books data similar to load_books_from_database
            self.books_data = []
            
            for book in sorted_books:
                try:
                    book_code = book.get("BookCode")
                    if not book_code:
                        continue
                    
                    # Find all authors for this book
                    book_authors_list = [
                        author["bookAuthor"] for author in book_authors 
                        if author.get("BookCode") == book_code and author.get("bookAuthor")
                    ]
                    
                    # Find all genres for this book
                    book_genres_list = [
                        genre["Genre"] for genre in book_genres 
                        if genre.get("BookCode") == book_code and genre.get("Genre")
                    ]
                    
                    # Use "Unknown" if no authors/genres found
                    if not book_authors_list:
                        book_authors_list = ["Unknown Author"]
                    if not book_genres_list:
                        book_genres_list = ["Unknown Genre"]
                    
                    # Create book data dictionary
                    book_data = {
                        "book_code": book_code,
                        "title": book.get("BookTitle", "Unknown Title"),
                        "author": book_authors_list,
                        "genre": book_genres_list,
                        "isbn": book.get("ISBN", ""),
                        "publisher": book.get("Publisher", "Unknown Publisher"), 
                        "description": book.get("BookDescription", ""),
                        "shelf": book.get("BookShelf", ""),  # Changed from BookShelf to BookShelf
                        "copies": book.get("BookTotalCopies", 0),
                        "available_copies": book.get("BookAvailableCopies", 0),
                        "image": book.get("BookCover", "")
                    }
                    
                    self.books_data.append(book_data)
                    
                except Exception as e:
                    print(f"Error processing sorted book {book}: {e}")
                    continue
            
            print(f"Successfully sorted {len(self.books_data)} books")
            
            # Update the title to show current sort
            sort_description = {
                "ascendingTitle": "Title (A-Z)",
                "descendingTitle": "Title (Z-A)",
                "ascendingAuthor": "Author (A-Z)", 
                "descendingAuthor": "Author (Z-A)",
                "mostCopies": "Most Copies",
                "leastCopies": "Least Copies"
            }
            
            current_sort = sort_description.get(filter_name, "Books Management")
            self.title_label.setText(f"Sorted by {current_sort}")
            
            # Refresh the display with sorted books
            self.populate_books()
            
        except Exception as e:
            print(f"Error sorting books: {e}")
            import traceback
            traceback.print_exc()

    def show_shelf_view(self):
        """Show books organized by shelf location"""
        # Create a popup menu with available shelves
        from PySide6.QtWidgets import QMenu
        
        shelf_menu = QMenu(self)
        shelf_menu.setStyleSheet("""
            QMenu {
                background-color: #FFFEF0;
                border: 2px solid #5C4033;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #5C4033;
                font-size: 14px;
            }
            QMenu::item:selected {
                background-color: #dbcfc1;
                border-radius: 4px;
            }
        """)
        
        # Get available shelves from database - include both shelves with books and empty shelves
        sorted_shelves = []  # Initialize empty list in case of error
        try:
            bookshelf_records = self.db_seeder.get_all_records("BookShelf", self.librarian_id or 1)

            # Extract ShelfId values from each record
            shelves_with_books = [row["ShelfId"] for row in bookshelf_records if "ShelfId" in row and row["ShelfId"]]

            sorted_shelves = sorted(set(shelves_with_books))
            print(f"✓ Found {len(sorted_shelves)} shelves for librarian {self.librarian_id}: {sorted_shelves}")

        except Exception as e:
            print(f"✗ Error fetching or sorting shelves: {e}")
            sorted_shelves = []  # Ensure we have an empty list on error

        # Add "All Books" option
        shelf_menu.addAction("All Books", lambda: self.display_shelf_books(None))
        
        # Add individual shelf options
        if sorted_shelves:
            shelf_menu.addSeparator()
            
            for shelf in sorted_shelves:
                shelf_menu.addAction(f"Shelf {shelf}", lambda s=shelf: self.display_shelf_books(s))
            print(f"✓ Added {len(sorted_shelves)} shelves to menu")
        else:
            # If no shelves are found
            no_shelves_action = shelf_menu.addAction("No shelves found")
            no_shelves_action.setEnabled(False)
            print(f"ℹ No shelves found for librarian {self.librarian_id}")

        # Show menu at button position
        shelf_menu.exec(self.shelf_button.mapToGlobal(self.shelf_button.rect().bottomLeft()))
        
    def display_shelf_books(self, shelf=None):
        """Display books for a specific shelf or all books if shelf is None"""
        if shelf is None:
            # Show all books - reload from database
            self.current_shelf = None
            self.delete_shelf_button.hide()
            self.load_books_from_database()
            self.title_label.setText("Books Management")
        else:
            self.current_shelf = shelf
            self.delete_shelf_button.show()
            # Filter books by shelf using database
            try:
                print(f"Filtering books by shelf: {shelf}")
                
                # Get filtered books from database
                shelf_books = self.db_seeder.filterBooks(shelf, self.librarian_id or 1)
                
                if not shelf_books:
                    self.books_data = []
                    self.title_label.setText(f"Books on Shelf {shelf}")
                    self.populate_books()
                    
                    from PySide6.QtWidgets import QMessageBox
                    msg = QMessageBox(self)
                    msg.setWindowTitle("Shelf View")
                    msg.setText(f"Shelf '{shelf}' is empty.\n\nTo add books to this shelf, use the '➕ Add Book' option and assign them to shelf '{shelf}'.")
                    msg.setIcon(QMessageBox.Information)
                    msg.setStyleSheet("""
                        QMessageBox {
                            background-color: white;
                            color: black;
                            font-weight: normal;
                        }
                        QLabel {
                            color: black;
                            font-weight: normal;
                            font-size: 14px;
                            background-color: transparent;
                            border: none;
                        }
                        QPushButton {
                            background-color: #5C4033;
                            color: white;
                            padding: 5px 15px;
                            border: none;
                            border-radius: 5px;
                            font-weight: normal;
                        }
                        QPushButton:hover {
                            background-color: #8B4513;
                        }
                    """)
                    msg.exec()
                    return
                
                # Get the authors and genres for the filtered books
                book_authors = self.db_seeder.get_all_records("BookAuthor", self.librarian_id or 1)
                book_genres = self.db_seeder.get_all_records("Book_Genre", self.librarian_id or 1)
                book_shelf = self.db_seeder.get_all_records("BookShelf", self.librarian_id or 1)
                
                # Process the filtered books data similar to load_books_from_database
                self.books_data = []
                
                for book in shelf_books:
                    try:
                        book_code = book.get("BookCode")
                        if not book_code:
                            continue
                        
                        # Find all authors for this book
                        book_authors_list = [
                            author["bookAuthor"] for author in book_authors 
                            if author.get("BookCode") == book_code and author.get("bookAuthor")
                        ]
                        
                        # Find all genres for this book
                        book_genres_list = [
                            genre["Genre"] for genre in book_genres 
                            if genre.get("BookCode") == book_code and genre.get("Genre")
                        ]
                        
                        # Use "Unknown" if no authors/genres found
                        if not book_authors_list:
                            book_authors_list = ["Unknown Author"]
                        if not book_genres_list:
                            book_genres_list = ["Unknown Genre"]
                        
                        # Create book data dictionary
                        book_data = {
                            "book_code": book_code,
                            "title": book.get("BookTitle", "Unknown Title"),
                            "author": book_authors_list,
                            "genre": book_genres_list,
                            "isbn": book.get("ISBN", ""),
                            "publisher": book.get("Publisher", "Unknown Publisher"), 
                            "description": book.get("BookDescription", ""),
                            "shelf": book.get("BookShelf", ""),  # Changed from BookShelf to BookShelf
                            "copies": book.get("BookTotalCopies", 0),
                            "available_copies": book.get("BookAvailableCopies", 0),
                            "image": book.get("BookCover", "")
                        }
                        
                        self.books_data.append(book_data)
                        
                    except Exception as e:
                        print(f"Error processing shelf book {book}: {e}")
                        continue
                
                self.title_label.setText(f"Books on Shelf {shelf}")
                print(f"Successfully filtered {len(self.books_data)} books from shelf {shelf}")
                
            except Exception as e:
                print(f"Error filtering books by shelf: {e}")
                self.books_data = []
                self.title_label.setText(f"Books on Shelf {shelf}")
        
        # Update display
        self.populate_books()

    def delete_current_shelf(self):
        """Delete the currently selected shelf"""
        from PySide6.QtWidgets import QMessageBox

        shelf = self.current_shelf
        if not shelf:
            return

        confirm = QMessageBox.question(
            self,
            "Delete Shelf",
            f"Are you sure you want to delete shelf '{shelf}'?\nAll books on this shelf will remain, but the shelf will be removed from the list.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                self.db_seeder.delete_table(tableName="BookShelf", column="ShelfId", value=shelf, librarian_id=self.librarian_id or 1)
                QMessageBox.information(self, "Success", f"Shelf '{shelf}' deleted.")
                self.current_shelf = None
                self.delete_shelf_button.hide()
                self.load_books_from_database()
                self.title_label.setText("Books Management")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to delete shelf: {e}")

    def create_main_books_view(self):
        """Create the main books view with search and grid"""
        view_widget = QWidget()
        view_layout = QVBoxLayout(view_widget)
        view_layout.setContentsMargins(40, 50, 40, 50)
        
        # Create header section with title and search button
        header_layout = QHBoxLayout()
        
        # Create title label
        self.title_label = QLabel("Books Management")
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.title_label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 50px;
                font-weight: bold;
                background-color: transparent;
                padding: 0px;
                margin: 0px;
            }
        """)
        # ...existing code...
        self.delete_shelf_button = QPushButton("🗑️")
        self.delete_shelf_button.setFixedSize(50, 50)
        self.delete_shelf_button.setToolTip("Delete This Shelf")
        self.delete_shelf_button.clicked.connect(self.delete_current_shelf)
        self.delete_shelf_button.setStyleSheet("""
            QPushButton {
                color: #CC4125;
                font-size: 20px;
                font-weight: bold;
                background-color: #F5F5F5;
                border: 3px solid #CC4125;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #CC4125;
                color: white;
            }
        """)
        self.delete_shelf_button.hide()  # Hide by default

        
        # Create search container
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        # Create search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search books...")
        self.search_bar.setFixedSize(300, 50)
        self.search_bar.returnPressed.connect(self.perform_search)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                color: #5C4033;
                font-size: 16px;
                padding: 10px 15px;
                background-color: #FFFEF0;
                border: 3px solid #5C4033;
                border-radius: 10px;
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: white;
            }
        """)
        
        # SEARCH BUTTON
        self.search_button = QPushButton("🔍")
        self.search_button.setFixedSize(50, 50)
        self.search_button.clicked.connect(self.perform_search)
        self.search_button.setStyleSheet("""
            QPushButton {
                color: #5C4033;
                font-size: 20px;
                font-weight: bold;
                background-color: #F5F5F5;
                border: 3px solid #5C4033;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5C4033;
                color: white;
            }
        """)

        # SORT BUTTON
        self.sort_button = QPushButton("🔄")
        self.sort_button.setFixedSize(50, 50)
        self.sort_button.setToolTip("Sort Books")
        self.sort_button.clicked.connect(self.show_sort_options)
        self.sort_button.setStyleSheet("""
            QPushButton {
                color: #5C4033;
                font-size: 20px;
                font-weight: bold;
                background-color: #F5F5F5;
                border: 3px solid #5C4033;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5C4033;
                color: white;
            }
        """)

        # BOOKSHELF BUTTON
        self.shelf_button = QPushButton("📚")
        self.shelf_button.setFixedSize(50, 50)
        self.shelf_button.setToolTip("View by Shelf")
        self.shelf_button.clicked.connect(self.show_shelf_view)
        self.shelf_button.setStyleSheet("""
            QPushButton {
                color: #5C4033;
                font-size: 20px;
                font-weight: bold;
                background-color: #F5F5F5;
                border: 3px solid #5C4033;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5C4033;
                color: white;
            }
        """)

        # ADD A BOOK BUTTON
        self.add_button = QPushButton("➕")
        self.add_button.setFixedSize(50, 50)
        self.add_button.clicked.connect(self.show_add_options)
        self.add_button.setStyleSheet("""
             QPushButton {
                color: #5C4033;
                font-size: 20px;
                font-weight: bold;
                background-color: #F5F5F5;
                border: 3px solid #5C4033;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #5C4033;
                color: white;
            }
        """)
        
        search_layout.addWidget(self.delete_shelf_button)
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
        search_layout.addWidget(self.sort_button)
        search_layout.addWidget(self.shelf_button)
        search_layout.addWidget(self.add_button)
        
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(search_container, alignment=Qt.AlignTop)
        
        view_layout.addLayout(header_layout)
        view_layout.addSpacerItem(QSpacerItem(20, 30, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Create books section
        self.books_container = self.create_books_section()
        view_layout.addWidget(self.books_container)
        
        view_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        return view_widget
    
    def show_add_options(self):
        """Show dropdown menu with Add Book and Add Shelf options"""
        add_menu = QMenu(self)
        add_menu.setStyleSheet("""
            QMenu {
                background-color: #FFFEF0;
                border: 2px solid #5C4033;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #5C4033;
                font-size: 14px;
            }
            QMenu::item:selected {
                background-color: #dbcfc1;
                border-radius: 4px;
            }
        """)
        
        # Add options
        add_menu.addAction("Add Book", self.show_add_book_dialog)
        add_menu.addAction("Add Shelf", self.show_add_shelf_dialog)
        
        # Show menu at button position
        add_menu.exec(self.add_button.mapToGlobal(self.add_button.rect().bottomLeft()))

    def show_add_shelf_dialog(self):
        """Show dialog to add a new bookshelf"""
        print(f"🔧 Opening Add Shelf dialog for LibrarianID: {self.librarian_id}")
        
        # Create the add shelf dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Shelf")
        dialog.setFixedSize(400, 350)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
            }
            QLabel {
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #dbcfc1;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #5C4033;
            }
            QLineEdit:focus {
                border-color: #5C4033;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        # Dialog layout
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Add New Bookshelf")
        title_label.setStyleSheet("font-size: 20px; margin-bottom: 30px;")
        layout.addWidget(title_label)
        
        # Shelf ID input with instructions
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
        save_btn.setStyleSheet("""
            background-color: #5C4033;
            color: white;
            min-width: 100px;
        """)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            background-color: white;
            color: #5C4033;
            border: 2px solid #5C4033;
            min-width: 100px;
        """)
        
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
                
        # Validate shelf ID format
        if not re.match(r'^[A-Z][0-9]{1,5}$', shelf_id):
            msg = QMessageBox(dialog)
            msg.setWindowTitle("Validation Error")
            msg.setText("Shelf ID must be one letter (A-Z) followed by 1-5 digits.\nExample: A1, B12, C345")
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                    font-weight: normal;
                }
                QLabel {
                    color: black;
                    font-weight: normal;
                    font-size: 14px;
                    background-color: transparent;
                    border: none;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: black;
                    padding: 5px 15px;
                    border: 1px solid #bbbbbb;
                    border-radius: 5px;
                    font-weight: normal;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
            msg.exec()
            return
        
        try:
           # Check for duplicate book in database
            exist = self.db_seeder.handleDuplication(tableName="BookShelf", librarianID= self.librarian_id, column="ShelfId", value=shelf_id)               
            
            if exist == True:
                msg = QMessageBox(dialog)
                msg.setWindowTitle("Duplicate Shelf")
                msg.setText(f"Shelf ID '{shelf_id}' already exists.")
                msg.setIcon(QMessageBox.Warning)
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                        color: black;
                        font-weight: normal;
                    }
                    QLabel {
                        color: black;
                        font-weight: normal;
                        font-size: 14px;
                        background-color: transparent;
                        border: none;
                    }
                    QPushButton {
                        background-color: #e0e0e0;
                        color: black;
                        padding: 5px 15px;
                        border: 1px solid #bbbbbb;
                        border-radius: 5px;
                        font-weight: normal;
                    }
                    QPushButton:hover {
                        background-color: #d0d0d0;
                    }
                """)
                msg.exec()
                return
            
            # Insert new shelf into database
            print(f"🔄 Attempting to save shelf '{shelf_id}' for LibrarianID: {self.librarian_id}")
            
            try:
                self.db_seeder.seed_data(
                    tableName="BookShelf",
                    data=[{"ShelfId": shelf_id, "LibrarianID": self.librarian_id or 1}], 
                    columnOrder=["ShelfId", "LibrarianID"]
                )
                print(f"✅ Successfully saved shelf '{shelf_id}' to database")
                
                # Verify it was actually inserted
                conn, cursor = self.db_seeder.get_connection_and_cursor()
                cursor.execute("SELECT * FROM BookShelf WHERE ShelfId = ? AND LibrarianID = ?", 
                            (shelf_id, self.librarian_id or 1))
                verification = cursor.fetchone()
                conn.close()
                
                if verification:
                    print(f"✅ Verification successful: Shelf found in database: {verification}")
                else:
                    print(f"❌ Verification failed: Shelf not found in database")
                    raise Exception("Shelf was not properly inserted into database")
                    
            except Exception as db_error:
                print(f"❌ Database error while saving shelf: {db_error}")
                raise db_error
            
            # Show success message
            success_msg = QMessageBox(dialog)
            success_msg.setWindowTitle("Success")
            success_msg.setText(f"Shelf '{shelf_id}' has been added successfully!\n\nYou can now find it in the 'View by Shelf' menu (📚 button) to sort books by this shelf.")
            success_msg.setIcon(QMessageBox.Information)
            success_msg.setStyleSheet("""
                QMessageBox {
                    background-color: white;
                    color: black;
                    font-weight: normal;
                }
                QLabel {
                    color: black;
                    font-weight: normal;
                    font-size: 14px;
                    background-color: transparent;
                    border: none;
                }
                QPushButton {
                    background-color: #5C4033;
                    color: white;
                    padding: 5px 15px;
                    border: none;
                    border-radius: 5px;
                    font-weight: normal;
                }
                QPushButton:hover {
                    background-color: #8B4513;
                }
            """)
            success_msg.exec()
            
            print(f"✅ Shelf '{shelf_id}' successfully added and verified in database")
            dialog.accept()
            
        except Exception as e:
            msg = QMessageBox(dialog)
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to add shelf: {str(e)}")
            msg.setIcon(QMessageBox.Critical)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #d0d0d0;
                    color: black;
                    font-weight: normal;
                }
                QLabel {
                    color: black;
                    font-weight: normal;
                    font-size: 14px;
                    background-color: transparent;
                    border: none;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: black;
                    padding: 5px 15px;
                    border: 1px solid #bbbbbb;
                    border-radius: 5px;
                    font-weight: normal;
                }
                QPushButton:hover {
                    background-color: #d0d0d0;
                }
            """)
            msg.exec()
            print(f"Error adding shelf: {e}")
            
    def perform_search(self):
        """Perform search with the text from search bar"""
        search_text = self.search_bar.text().strip().lower()
        if search_text:
            print(f"Searching for: '{search_text}'")
            filtered_books = []
            
            for book in self.original_books_data:
                # Search in title
                title_match = search_text in book['title'].lower()
                
                # Search in authors (handle list of authors)
                author_match = False
                if isinstance(book['author'], list):
                    author_match = any(search_text in author.lower() for author in book['author'])
                else:
                    author_match = search_text in str(book['author']).lower()
                
                # Search in genres (handle list of genres)
                genre_match = False
                if isinstance(book['genre'], list):
                    genre_match = any(search_text in genre.lower() for genre in book['genre'])
                else:
                    genre_match = search_text in str(book['genre']).lower()
                
                # Search in ISBN
                isbn_match = search_text in str(book.get('isbn', '')).lower()
                
                if title_match or author_match or genre_match or isbn_match:
                    filtered_books.append(book)
            
            self.books_data = filtered_books
            print(f"Found {len(filtered_books)} matching books")
        else:
            # Restore original list when search is cleared
            self.books_data = self.original_books_data.copy()
            print(f"Restored {len(self.books_data)} books")
        
        self.populate_books()

    def create_books_section(self):
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
        """Populate the books grid"""
        print(f"Populating {len(self.books_data)} books...")
        # Clear existing widgets
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
    
        # Add books to grid (4 books per row with larger cards)
        columns_per_row = 6
        for index, book in enumerate(self.books_data):
            row = index // columns_per_row
            col = index % columns_per_row            
            book_card = self.create_book_card(book)
            self.grid_layout.addWidget(book_card, row, col)
    
    def create_book_card(self, book_data):
        """Create a clickable book card"""
        card_widget = QPushButton()
        card_widget.setFixedSize(200, 280)
        card_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card_widget.clicked.connect(lambda checked, data = book_data: self.show_book_preview(data))
        card_widget.setStyleSheet("""
            QPushButton {
                background-color: #f8f8f8;
                border-radius: 12px;
                border: 2px solid #e0e0e0;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #5C4033;
            }
            QPushButton:pressed {
                background-color: #e8e8e8;
            }
        """)
        
        # Create a layout for the button content
        card_layout = QVBoxLayout(card_widget)
        card_layout.setContentsMargins(10, 10, 10, 8)
        card_layout.setSpacing(8)
        
        # Book cover image
        book_cover = QLabel()
        book_cover.setFixedSize(150, 200)
        book_cover.setAlignment(Qt.AlignCenter)
        book_cover.setStyleSheet("""
            QLabel {
                background-color: #dbcfc1;
                border-radius: 8px;
                border: 2px solid #5C4033;
            }
        """)
        # Try to load image
        image_path = book_data.get("image", "")
        print(f"Book: {book_data['title']}, Image path: {image_path}, Type: {type(image_path)}")
        if image_path and isinstance(image_path, str) and os.path.exists(image_path):
            try:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        QSize(150, 200),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    book_cover.setPixmap(scaled_pixmap)
                    book_cover.setStyleSheet("""
                        QLabel {
                            border-radius: 8px;
                            border: 2px solid #5C4033;
                        }
                    """)
                    print(f"Loaded image: {image_path}")
                else:
                    print(f"Invalid image: {image_path}")
            except Exception as e:
                print(f"Error loading image for {book_data['title']}: {e}")
        
        # Book title
        title_label = QLabel(book_data["title"])
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(35)
        title_label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
                border: none;
                padding: 2px;
            }
        """)
        
        # Book author - handle list of authors
        authors = book_data["author"]
        if isinstance(authors, list):
            author_text = ', '.join(authors[:2])  # Show max 2 authors
            if len(authors) > 2:
                author_text += f" +{len(authors)-2} more"
        else:
            author_text = str(authors)
            
        author_label = QLabel(author_text)
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setWordWrap(True)
        author_label.setMaximumHeight(25)
        author_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                font-size: 12px;
                background-color: transparent;
                border: none;
                padding: 1px;
            }
        """)
        
        card_layout.addWidget(book_cover, alignment=Qt.AlignCenter)
        card_layout.addWidget(title_label)
        card_layout.addWidget(author_label)
        
        return card_widget 
    
    def show_book_preview(self, book_data):
        """Show book preview dialog"""
        preview_dialog = BookPreviewDialog(book_data, self)
        preview_dialog.exec()
    
    def open_book_edit(self, book_data):
        """Open the book edit view"""
        # Clear current content
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Create and show edit view
        self.book_edit_view = BookEditView(book_data, self)
        self.content_layout.addWidget(self.book_edit_view)
        self.current_view = "edit"
    
    def show_books_view(self):
        """Show the main books view"""
        # Clear current content
        for i in reversed(range(self.content_layout.count())):
            child = self.content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Refresh books display and show main view
        self.load_books_from_database()
        self.content_layout.addWidget(self.main_books_view)
        self.current_view = "books"
      # def close_tab(self, index):
   #     """Close a tab"""    
   #    if index > 0:  # Don't close the main books tab
    #        self.tab_widget.removeTab(index)
    
    def show_book_edit_view(self, book_data):
        """Show the book edit view in the main window"""
        print(f"[DEBUG] show_book_edit_view called with book: {book_data}")
        print(f"[DEBUG] Book title: {book_data.get('title', 'unknown')}")
        try:
            # Remove current view and show BookEditView
            for i in reversed(range(self.content_layout.count())):
                widget = self.content_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            edit_view = BookEditView(book_data, self)
            self.content_layout.addWidget(edit_view)
            self.current_view = "edit"
            print("[DEBUG] BookEditView added to content_layout")
        except Exception as e:
            print(f"[ERROR] Exception in show_book_edit_view: {e}")
            import traceback
            traceback.print_exc()

    def refresh_books_display(self):
        self.load_books_from_database()

    def show_add_book_dialog(self):
        """Show the book add dialog"""

        dialog = AddBookDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Refresh the display after adding a book
            self.load_books_from_database()
