import os
import re
import sys
import requests
import shutil
from navbar_logic import nav_manager
from navigation_sidebar import NavigationSidebar
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QTimer
from PySide6.QtGui import QFont, QIcon, QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QLineEdit, QScrollArea, QGridLayout,
    QTabWidget, QTextEdit, QMessageBox, QFormLayout, QDialog, QListWidget,
    QListWidgetItem, QGroupBox, QSpinBox, QFileDialog
)

from tryDatabase import DatabaseSeeder  #to connect to databse seeder

#THERE ARE 4 CLASSES HERE:
# 1. BookEditView: for editing book details
# 2. AddBookDialog: for adding new book
# 3. BookDetailsDialog: for showing book details and manual entry
# 4. Collapsible Sidebar: MAIN WINDOW

class BookEditView(QWidget):
    def __init__(self, book_data, parent_window):
        super().__init__()
        self.book_data = book_data 
        self.parent_window = parent_window
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        # Back button and title section
        header_layout = QHBoxLayout()
        
        # Back button
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
        
        # Title
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
        
        # Create form layout
        form_widget = QWidget()
        form_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 16px;
                border: 2px solid #dbcfc1;
            }
        """)
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        # Book details form - Read-only fields
        self.title_input = QLineEdit(self.book_data['title'])
        self.title_input.setReadOnly(True)
        self.title_input.setStyleSheet(self.get_readonly_input_style())
        
        author = self.book_data['author']
        if isinstance(author, list):
            author = ', '.join(author)
        self.author_input = QLineEdit(author)
        self.author_input.setReadOnly(True)
        self.author_input.setStyleSheet(self.get_readonly_input_style())
        
        genre = self.book_data['genre']
        if isinstance(genre, list):
            genre = ', '.join(genre)
        self.genre_input = QLineEdit(genre)
        self.genre_input.setReadOnly(True)
        self.genre_input.setStyleSheet(self.get_readonly_input_style())
        
        self.isbn_input = QLineEdit(self.book_data.get('isbn', ''))
        self.isbn_input.setReadOnly(True)
        self.isbn_input.setStyleSheet(self.get_readonly_input_style())
       
        # Editable fields
        self.copies_input = QLineEdit(str(self.book_data.get('copies', '1')))
        self.copies_input.setStyleSheet(self.get_editable_input_style())
        
        self.shelf_input = QLineEdit(self.book_data.get('shelf', ''))
        self.shelf_input.setStyleSheet(self.get_editable_input_style())
        
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
                border-color: #5C4033;
            }
        """)
        
        # Add fields to form
        form_layout.addRow(self.create_label("Title:"), self.title_input)
        form_layout.addRow(self.create_label("Author:"), self.author_input)
        form_layout.addRow(self.create_label("Genre:"), self.genre_input)
        form_layout.addRow(self.create_label("ISBN:"), self.isbn_input)
        form_layout.addRow(self.create_label("Available copy of books:"), self.copies_input)
        form_layout.addRow(self.create_label("Shelf No.:"), self.shelf_input)
        form_layout.addRow(self.create_label("Description:"), self.description_input)
        
        layout.addWidget(form_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Save button
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
    
    def save_changes(self): #saves book
        if not self.copies_input.text().isdigit() or int(self.copies_input.text()) < 1: #check if copies if positive number
            QMessageBox.warning(self, "Validation Error", "Copies must be a positive integer")
            return
        try:
            # Update book data
            self.book_data['copies'] = int(self.copies_input.text())
            self.book_data['available_copies'] = int(self.copies_input.text())
            self.book_data['shelf'] = self.shelf_input.text()
            self.book_data['description'] = self.description_input.toPlainText()
            
            # Show confirmation
            msg = QMessageBox()
            msg.setWindowTitle("Success")
            msg.setText(f"Book '{self.book_data['title']}' has been updated successfully!")
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            self.parent_window.show_books_view() # Go back to main books view
        except:
            QMessageBox.warning(self, "Error", "Error updating books: {e}")
            print(f"Error updating books: {e}")  
              
    def delete_book(self):
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            'Confirm Deletion', 
            f"Are you sure you want to delete '{self.book_data['title']}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from books data
            if self.book_data in self.parent_window.books_data:
                self.parent_window.books_data.remove(self.book_data)
            
            # Show confirmation
            msg = QMessageBox()
            msg.setWindowTitle("Deleted")
            msg.setText(f"Book '{self.book_data['title']}' has been deleted successfully!")
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            
            # Go back to main books view
            self.parent_window.show_books_view()
    
    def go_back(self):
        # Go back to main books view without saving
        self.parent_window.show_books_view()

class AddBookDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.db_seeder = DatabaseSeeder()
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
        info_layout.setSpacing(15)

        # Section Title
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
    
    def validate_isbn(self, isbn): # check isbn len
        isbn_clean = re.sub(r'[^0-9X]', '', isbn.upper()) #remove  special characters, allows X

        if len(isbn_clean) not in [10, 13]: #check length if its 10 or 13
            return False
        if len(isbn_clean) == 10:
            return self.validate_isbn10(isbn_clean) #pass isbn10 to validate 
        return self.validate_isbn13(isbn_clean) #pass isbn13 to validate
    
    def validate_isbn10(self, isbn):
        if len(isbn)!= 10:
            return False
        total = 0 
        for i in range(9): #calculate checksum (each digit multipled by its position)
            if not isbn[i].isdigit():
                return False
            total += int(isbn[i]) * (10 - i) 
        if isbn[9] == 'X': # X represents 10, so add 10 to total
            total += 10
        elif isbn[9].isdigit():
            total += int(isbn[9])
        else:
            return False
        return total % 11 == 0 #valid if totals is divisible by 11
    
    def validate_isbn13(self, isbn):
        if len(isbn) != 13:
            return False
        if not isbn.isdigit():
            return False 
        total = 0 
        for i in range(12): #calculate checksum (alternate bewteen 1 and 3 multipliers)
            if i % 2 == 0:
                total += int(isbn[i])
            else:
                total += int(isbn[i]) *3
        check_digit = (10 - (total % 10)) % 10
        return check_digit == int(isbn[12]) #valid f last digit is matched with the check digit
    
    def reset_cover_preview(self):
        self.book_preview.setPixmap(QPixmap()) #clear book cover image
        self.book_preview.setText("Book Cover Preview")   
        self.book_preview.setStyleSheet(""" #preview box layout
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

        # Validate ISBN 
        if isbn and not self.validate_isbn(isbn):
            QMessageBox.warning(self,"Invalid ISBN","The provided ISBN is invalid. Please correct the ISBN"
            )
            self.found_book_data = None
            self.reset_cover_preview() 
            return
        try:
            self.reset_cover_preview() #clear preview book preview
            API_KEY = os.getenv('GOOGLE_BOOKS_API_KEY', 'AIzaSyBk4UqlqwPwSQwhdLQfOG5-Z-S3L7oTtYY')
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
        details_dialog = BookDetailsDialog(
            parent = self,
            book_data = book_data,
            is_found_book =False #allow edit all fields
        )
        if details_dialog.exec() ==QDialog.Accepted:
            standardized_book = {
                'title': details_dialog.book_data['title'],
                'author': details_dialog.book_data['author'],
                'isbn': details_dialog.book_data['isbn'],
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
        title = self.title_input.text().strip() #get input values
        author = self.author_input.text().strip()
        isbn = re.sub(r'[^0-9X]', '', self.isbn_input.text().strip().upper())

        if not title or not author or not isbn: #require three fields for input
            QMessageBox.information(self, "Adding book Error", "Please fill in all required fields: Title, Author, and ISBN")
            return
        if isbn and not self.validate_isbn(isbn): #check if isbn is valid
            QMessageBox.warning(self, "Validation Error", "Invalid ISBN")
            return

        book_data = self.found_book_data or { #use found book data or create manually
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
        details_dialog = BookDetailsDialog( # for futher inputs
            parent=self,
            book_data=book_data,
            is_found_book=bool(self.found_book_data)
        )
        if details_dialog.exec() == QDialog.Accepted:
            standardized_book = { #book format and details
                'title': details_dialog.book_data['title'],
                'author': details_dialog.book_data['author'],
                'isbn': details_dialog.book_data['isbn'],
                'genre': details_dialog.book_data['genre'],
                'description': details_dialog.book_data['description'],
                'shelf': details_dialog.book_data['shelf'],
                'copies': details_dialog.book_data['copies'],
                'image': details_dialog.book_data.get('image', ''),
                'available_copies': details_dialog.book_data['available_copies']
            }
            print(f"Adding book to books_data: {standardized_book}")
            self.parent.books_data.append(standardized_book) #create parent wqindow for book list
            self.parent.refresh_books_display() #refresh display
            self.accept()

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
        self.setFixedSize(600, 700)
        self.setStyleSheet('''
            QDialog {
                background-color: #f1efe3;
                font-size: 14px;
            }
        ''')
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)

        title_label = QLabel("Enter Book Details")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #5C4033;
                margin-bottom: 5px;
                background: transparent;
            }
        """)
        main_layout.addWidget(title_label, alignment=Qt.AlignTop)
        
        # Input fields
        input_style = """
            QLineEdit, QTextEdit, QSpinBox {
                background-color: white;
                border: 1px solid #dbcfc1;
                border-radius: 5px;
                padding: 6px;
                font-size: 14px;
                color: #5C4033;
                min-height: 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QSpinBox:focus {
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
                min-height: 40px;
            }
        """
        # Label style with background
        label_style = """
            QLabel {
                color: #5C4033;
                font-size: 13px;
                font-weight: bold;
                background-color: #f9f9f9;
                border: 1px solid #dbcfc1;
                border-radius: 8px;
                padding: 3px 8px;
                margin-right: 8px;
            }
        """
        #book information group
        info_group = QGroupBox("Book Information")
        info_group.setStyleSheet("""
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
                left:8px;
                padding: 0 3px;
            }
        """)
        info_layout = QFormLayout(info_group)
        info_layout.setContentsMargins(12, 15, 12, 12)
        info_layout.setVerticalSpacing(6)
        info_layout.setHorizontalSpacing(8)
        
        # Form fields
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter Title")
        self.title_edit.setStyleSheet(input_style)
        self.title_edit.setFixedHeight(32)
        
        self.author_edit = QLineEdit()
        self.author_edit.setPlaceholderText("Enter Author")
        self.author_edit.setStyleSheet(input_style)
        self.author_edit.setFixedHeight(32)
        
        self.isbn_edit = QLineEdit()
        self.isbn_edit.setPlaceholderText("Enter ISBN")
        self.isbn_edit.setStyleSheet(input_style)
        self.isbn_edit.setFixedHeight(32)
        
        self.publisher_edit = QLineEdit()
        self.publisher_edit.setPlaceholderText("Enter Publisher")
        self.publisher_edit.setStyleSheet(input_style)
        self.publisher_edit.setFixedHeight(32)
        
        self.genre_edit = QLineEdit()
        self.genre_edit.setPlaceholderText("Enter Genre")
        self.genre_edit.setStyleSheet(input_style)
        self.genre_edit.setFixedHeight(32)
        
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Enter Description")
        self.description_edit.setStyleSheet(input_style)
        self.description_edit.setMinimumHeight(30)

        if self.is_found_book:
            self.title_edit.setReadOnly(True)
            self.author_edit.setReadOnly(True)
            self.isbn_edit.setReadOnly(True)
            self.publisher_edit.setReadOnly(True)
            if self.book_data.get('categories', ['N/A'])[0] != 'N/A':
                self.genre_edit.setReadOnly(True)
        else:
            self.title_edit.setReadOnly(False)
            self.author_edit.setReadOnly(False)
            self.isbn_edit.setReadOnly(False)
            self.publisher_edit.setReadOnly(False)
            self.genre_edit.setReadOnly(False)
        
        # Create and style labels
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
        info_layout.addRow(genre_label, self.genre_edit)
        info_layout.addRow(description_label, self.description_edit)

        main_layout.addWidget(info_group)

        #for book cover
        image_group = QGroupBox("Book Cover")
        image_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #dbcfc1;
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                background: transparent;
            }
        """)

        image_layout = QHBoxLayout(image_group)
        image_layout.setContentsMargins(10, 10, 10, 10)
        image_layout.setSpacing(10)

        image_container = QWidget()
        image_container_layout = QVBoxLayout(image_container)
        image_container_layout.setContentsMargins(0,0,0,0)
        image_container_layout.setSpacing(10)

        self.image_preview = QLabel()
        self.image_preview.setFixedSize(self.image_preview_size)
        self.image_preview.setMinimumSize(160, 200)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("")
        
        image_container_layout.addWidget(self.image_preview, alignment=Qt.AlignCenter)

        self.image_label = QLabel("No image selected")
        self.image_label.setAlignment(Qt.AlignCenter)
        image_container_layout.addWidget(self.image_label)

        image_layout.addWidget(image_container)

        self.image_btn = QPushButton("Upload Cover")
        self.image_btn.clicked.connect(self.upload_image)
        self.image_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C4033;
                color: white;
                padding: 8px 12px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        image_layout.addWidget(self.image_btn, alignment=Qt.AlignCenter)

        if self.is_found_book and self.book_data.get('image'):
            self.load_cover_preview()

        main_layout.addWidget(image_group)

        lib_group= QGroupBox("Library Information")
        lib_group.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border-radius: 15px;
                border: 2px solid #dbcfc1;
                color: #5C4033;
                font-size: 16px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0px 5px;
                background: transparent;
            }
        """)
        lib_layout = QFormLayout(lib_group)
        lib_layout.setContentsMargins(15, 20, 15, 15)
        lib_layout.setVerticalSpacing(10)
        lib_layout.setHorizontalSpacing(10)

        self.shelf_edit= QLineEdit()
        self.shelf_edit.setPlaceholderText("e.g., A1, B2")
        self.shelf_edit.setStyleSheet(input_style)
        self.shelf_edit.setFixedHeight(30)

        self.copies_spin = QSpinBox()
        self.copies_spin.setMaximum(999)
        self.copies_spin.setMinimum(1)
        self.copies_spin.setValue(1)
        self.copies_spin.setStyleSheet(input_style)
        self.copies_spin.setFixedHeight(30)

        # Create and style library info labels
        shelf_label = QLabel("Shelf Number:")
        shelf_label.setStyleSheet(label_style)
        copies_label = QLabel("Total Copies:")
        copies_label.setStyleSheet(label_style)

        lib_layout.addRow(shelf_label, self.shelf_edit)
        lib_layout.addRow(copies_label, self.copies_spin)

        main_layout.addWidget(lib_group)

        # save and cancel buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save Book")
        save_btn.clicked.connect(self.save_book)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5C4033;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                min-width: 120px;
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
                padding: 10px;
                border: 2px solid #5C4033;
                border-radius: 10px;
                font-size: 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
        """)
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

    def load_cover_preview(self):
        try:
            image_path = os.path.normpath(self.book_data['image']) #get local image file
            pixmap = QPixmap(image_path) #use qpixmap to load
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled( #resize image to fit preview
                    self.image_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled_pixmap)
                self.image_preview.setScaledContents(True) #pixmap automatically scale to preview size
                self.image_label.setText(f"Image: {os.path.basename(image_path)}") #display name of the imagefile below
            else:
                self.image_preview.setText("") #if failed to load image, clear preview area
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

    def populate_fields(self): #fill form fields with book data
        self.title_edit.setText(self.book_data.get('title', ''))
        author = self.book_data.get('author', '')
        if isinstance(author, list): # for response for author is list
            author = ', '.join(author)
        self.author_edit.setText(author)
        self.isbn_edit.setText(self.book_data.get('isbn', ''))
        self.publisher_edit.setText(self.book_data.get('publisher', ''))
        self.genre_edit.setText(','.join(self.book_data.get('categories', [''])))
        self.description_edit.setText(self.book_data.get('description', ''))

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName( #open file for user to upload image
            self, "Select Book Cover", "", "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path: #process only if file was selected
            try:
                if not os.path.exists('assets'): #create assests folder
                    os.makedirs('assets')
                isbn = re.sub(r'[^0-9X]', '', self.isbn_edit.text().strip().upper()) or 'temp' #isbn for filenames
                filename = f"book_cover_{isbn}.png"
                image_path = os.path.normpath(os.path.join('assets', filename)) #full path to dave the image
                shutil.copy(file_path, image_path) #copy the imaget= tot the folder
                print(f"Image copied to: {image_path}, Exists: {os.path.exists(image_path)}")
                if os.path.exists(image_path):
                    self.book_data['image'] = image_path #save image to book data
                    self.image_label.setText(f"Image: {os.path.basename(image_path)}")
                    pixmap = QPixmap(image_path) #load image in preview
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            self.image_preview.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.image_preview.setPixmap(scaled_pixmap)
                        self.image_preview.setStyleSheet("")
                    else: # for invald image
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
                else: #fallback for copy error
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
            ('Shelf Number', lambda: self.shelf_edit.text().strip(), "Shelf number is required", None),
        ]
        isbn = re.sub(r'[^0-9X]', '', self.isbn_edit.text().strip().upper()) #clean isbn
        if isbn and not self.parent.validate_isbn(isbn): #validate isbn
            QMessageBox.warning(self, "Validation Error", "Invalid ISBN")
        shelf = self.shelf_edit.text().strip()
        if not re.match(r'^[A-Z][0-9]{1,5}$', shelf):
            QMessageBox.warning(self, "Validation Error", "Shelf number must be one letter (A-Z) followed by 1 to 5 digits. (e.g. A1, B12, C345)")
            return
        for field_name , getter, error_msg, validator in fields:
            value = getter()
            if not value or (validator and not validator(value)):
                QMessageBox.warning(self, "Validation Error", error_msg)
                return
        authors = list(set([a.strip() for a in self.author_edit.text().strip().split(',') if a.strip()]))
        genres = list(set([g.strip() for g in self.genre_edit.text().strip().split(',') if g.strip()]))
        if not genres:
            QMessageBox.warning(self, "Validation Error", "At least one(1) genre is required")
            return
        try:
            self.book_data = { #store book infos in a disctionary
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
                'image_url' : self.book_data.get('image_url', '')
            }
            print(f"Saving book: {self.book_data}") #for debudding 
            QMessageBox.information(self, "Success", f"Book '{self.book_data['title']}' has been added to the library")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", "Unexpected Error: {e}")
            print(f"Unexpected Error: {e}")

#MAIN WINDOW
class CollapsibleSidebar(QWidget):
    def __init__(self):
        super().__init__()
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
        
        # Keep track of current view
        #self.current_view = "books"
        self.sidebar = NavigationSidebar()
        self.sidebar.on_navigation_clicked = nav_manager.handle_navigation

        
        # Combine sidebar and content area
        main_layout = QHBoxLayout(self)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_area)


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
        
        # ADD A BOOK BUTTON
        self.add_button = QPushButton("➕")
        self.add_button.setFixedSize(50, 50)
        self.add_button.clicked.connect(self.show_add_book_dialog)
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
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
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

    def perform_search(self):
        """Perform search with the text from search bar"""
        search_text = self.search_bar.text().strip().lower()
        if search_text:
            print(f"Searching for: {search_text}")
            filtered_books = [ #search item in the books
                book for book in self.original_books_data
                if search_text in book['title'].lower() or # for 1 author
                search_text in ', '.join(book['author']).lower() # for searching author in a list
            ]
            self.books_data = filtered_books #display found books
            self.populate_books()
        else:
            self.books_data = self.books_data #restore original list if needed
            self.populate_books()

    def create_books_section(self):
        """Create the books display section with multiple columns and vertical scrolling"""
        books_container = QWidget()
        books_container.setMinimumHeight(500)
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
        
        # Section title
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
        self.grid_layout.setSpacing(25)
        self.grid_layout.setContentsMargins(15, 15, 15, 15)
        
        # Populate books
        self.populate_books()
        
        scroll_area.setWidget(self.scroll_content)
        books_layout.addWidget(scroll_area)
        
        return books_container
    
    def populate_books(self):
        """Populate the books grid"""
        # Clear existing widgets
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
        
        # Add books to grid (5 books per row)
        columns_per_row = 5
        for index, book in enumerate(self.books_data):
            row = index // columns_per_row
            col = index % columns_per_row
            
            book_card = self.create_book_card(book)
            self.grid_layout.addWidget(book_card, row, col)
    
    def create_book_card(self, book_data):
        """Create a clickable book card"""
        card_widget = QPushButton()
        card_widget.setFixedSize(180, 240)
        card_widget.clicked.connect(lambda checked, data = book_data: self.open_book_edit(data))
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
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)
        
        # Book cover image
        book_cover = QLabel()
        book_cover.setFixedSize(120, 160)
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
                        QSize(120, 160),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                    book_cover.setPixmap(scaled_pixmap)
                    book_cover.setStyleSheet("")
                    print(f"Loaded image: {image_path}")
                else:
                    print(f"Invalid image: {image_path}")
            except Exception as e:
                print(f"Error loading image for {book_data['title']}: {e}")
        
        # Book title
        title_label = QLabel(book_data["title"])
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 13px;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
                                  
        """)
        # Book author
        author = book_data["author"]
        if isinstance(author, list):
            author = ', '.join(author)
        author_label = QLabel(author)
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setWordWrap(True)
        author_label.setStyleSheet("""
            QLabel {
                color: #8B4513;
                font-size: 13px;
                background-color: transparent;
                border: none;
            }
        """)
        
        card_layout.addWidget(book_cover, alignment=Qt.AlignCenter)
        card_layout.addWidget(title_label)
        card_layout.addWidget(author_label)
        card_layout.addStretch()
        
        return card_widget
    
    def open_book_edit(self, book_data):
        """Open the book edit view"""
        # Clear current content
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        # Create and show edit view
        self.book_edit_view = BookEditView(book_data, self)
        self.content_layout.addWidget(self.book_edit_view)
        self.current_view = "edit"
    
    def show_books_view(self):
        """Show the main books view"""
        # Clear current content
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
        
        # Refresh books display and show main view
        self.populate_books()
        self.content_layout.addWidget(self.main_books_view)
        self.current_view = "books"
    
    def close_tab(self, index):
        """Close a tab"""
        if index > 0:  # Don't close the main books tab
            self.tab_widget.removeTab(index)

    def refresh_books_display(self):
        """Refresh the books display after changes"""
        self.original_books_data = self.books_data.copy()
        self.populate_books()

    def show_add_book_dialog(self):
        """Show the book add dialog"""
        dialog = AddBookDialog(self)
        dialog.exec()

# Run app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Times New Roman", 10))
    window = CollapsibleSidebar()
    nav_manager._current_window = window  # Set as current window
    window.show()
    app.exec()