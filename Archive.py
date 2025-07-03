import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QPushButton, QFrame, 
                              QStackedWidget, QTableWidget, QTableWidgetItem,
                              QHeaderView, QLineEdit, QMessageBox, QDialog,
                              QFormLayout, QDateEdit, QComboBox, QSpacerItem,
                              QSizePolicy, QCheckBox)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont, QColor, QIcon
from datetime import datetime, timedelta
from navigation_sidebar import NavigationSidebar
from navbar_logic import nav_manager
from tryDatabase import DatabaseSeeder

class ArchiveManager(QMainWindow):
    def __init__(self, librarian_id=None):
        super().__init__()
        self.db_seeder = DatabaseSeeder()
        self.librarian_id = librarian_id
        
        self.setStyleSheet("""
            ArchiveManager {
                background-color: #f1efe3;
            }
        """)
        # Define button styles as class attributes
        self.button_base_style = """
            QPushButton {
                background-color: transparent;
                color: #8B4513;
                font-weight: normal;
                border-radius: 20px;
                border: 2px solid #e8d8bd;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #f5f3ed;
                border-color: #8B4513;
            }
        """

        self.button_active_style = """
            QPushButton {
                background-color: #5e3e1f;
                color: white;
                font-weight: bold;
                border-radius: 20px;
                border: 2px solid #5e3e1f;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5e3e1f;
                border-color: #5e3e1f;
            }
        """
        
        # Setup window properties
        self.setWindowTitle("Archive Management")
        self.setGeometry(100, 100, 1400, 800)
        self.showMaximized()
        
        # Initialize UI components
        self.setup_ui()
        
    def setup_ui(self):
        # Create main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main horizontal layout for sidebar + content
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 40, 20, 20)
        main_layout.setSpacing(0)
        
        # Add sidebar
        self.sidebar = NavigationSidebar()
        self.sidebar.navigation_clicked.connect(
            lambda item_name: nav_manager.handle_navigation(item_name, self.librarian_id)
        )
        main_layout.addWidget(self.sidebar)
        
        # Create content area widget with brown theme
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f1efe3;")
        main_layout.addWidget(content_widget)
        
        # Content layout (vertical)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Header with title
        header_widget = QWidget()
        header_widget.setFixedHeight(100)
        header_widget.setStyleSheet("background-color: #f1efe3;")
        content_layout.addWidget(header_widget)
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 20, 40, 20)
        
        title_label = QLabel("Archive Management")
        title_label.setFont(QFont("Times New Roman", 32, QFont.Bold))
        title_label.setStyleSheet("color: #5e3e1f;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Tab navigation buttons
        nav_widget = QWidget()
        nav_widget.setFixedHeight(60)
        nav_widget.setStyleSheet("background-color: #f1efe3;") 
        content_layout.addWidget(nav_widget)
        
        # FOR HORIZONTAL OF MEMBERS AND BOOKS ARCHIVE
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(80, 10, 200, 10)
        nav_layout.setSpacing(50)
        
        # Books Archive button
        self.books_btn = QPushButton("Archive Books")
        self.books_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.books_btn.setFixedSize(180, 40)
        self.books_btn.setStyleSheet(self.button_base_style)
        self.books_btn.clicked.connect(self.show_books_archive)
        nav_layout.addWidget(self.books_btn)

        # Shelf Archive button
        self.shelf_btn = QPushButton("Archive Shelf")
        self.shelf_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.shelf_btn.setFixedSize(180, 40)
        self.shelf_btn.setStyleSheet(self.button_base_style)
        self.shelf_btn.clicked.connect(self.show_shelf_archive)
        nav_layout.addWidget(self.shelf_btn)

        # Members Archive button
        self.members_btn = QPushButton("Archive Members")
        self.members_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.members_btn.setFixedSize(180, 40)
        self.members_btn.setStyleSheet(self.button_base_style)
        self.members_btn.clicked.connect(self.show_members_archive)
        nav_layout.addWidget(self.members_btn)
        
        nav_layout.setAlignment(Qt.AlignCenter)
        
        # Stacked widget for content pages
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        # Create pages
        self.create_books_archive_page()
        self.create_shelf_archive_page()  
        self.create_members_archive_page()
        
        # Show books archive by default
        self.show_books_archive()
        
    def create_books_archive_page(self):
        """Create the books archive page"""
        self.books_page = QWidget()
        self.books_page.setStyleSheet("background-color: #f1efe3;")
        
        layout = QVBoxLayout(self.books_page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.books_search = QLineEdit()
        self.books_search.setPlaceholderText("Search archived books...")
        self.books_search.setFont(QFont("Times New Roman", 12))
        self.books_search.setFixedHeight(35)
        self.books_search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e8d8bd;
                border-radius: 10px;
                background-color: #fff;
                color: #5e3e1f;
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: #f5f3ed;
            }
        """)
        self.books_search.textChanged.connect(self.search_archived_books)
        search_layout.addWidget(self.books_search)
        
        
        layout.addLayout(search_layout)
        
        # Books archive table with description removed
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(9)  
        self.books_table.setHorizontalHeaderLabels([
            "Date Deleted","Book Code", "Title", "Author", "Genre", "ISBN", 
            "Copies", "Shelf", "Select"
        ])

        header = self.books_table.horizontalHeader()
        for i in range(8):  # First 7 columns stretch
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(7, QHeaderView.Fixed)  
        self.books_table.setColumnWidth(7, 150)  
    
        self.books_table.verticalHeader().setVisible(False)
        self.books_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.books_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.books_table.setAlternatingRowColors(True)
        self.books_table.setShowGrid(True)
        self.setup_table_style(self.books_table)
        
        layout.addWidget(self.books_table, stretch=1)
        
        self.content_stack.addWidget(self.books_page)
        
        # Load archived books data
        self.load_archived_books()
        
    def create_members_archive_page(self):
        """Create the members archive page"""
        self.members_page = QWidget()
        self.members_page.setStyleSheet("background-color: #f1efe3;")
        
        
        layout = QVBoxLayout(self.members_page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.members_search = QLineEdit()
        self.members_search.setPlaceholderText("Search archived members...")
        self.members_search.setFont(QFont("Times New Roman", 12))
        self.members_search.setFixedHeight(35)
        self.members_search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                background-color: white;
                color: #5C4033;
            }
            QLineEdit:focus {
                border-color: #e8d8bd;
                background-color: white;
            }
        """)
        self.members_search.textChanged.connect(self.search_archived_members)
        search_layout.addWidget(self.members_search)
        
        
        layout.addLayout(search_layout)
        
        # Members archive table with updated columns
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(7)
        self.members_table.setHorizontalHeaderLabels([
          "Date Deleted",  "Member ID", "First Name", "Middle Name", "Last Name", "Contact Number", "Select"
        ])
        
        
        header = self.members_table.horizontalHeader()
        for i in range(6):  # First 5 columns stretch
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)  
        self.members_table.setColumnWidth(5, 150) 
    
        self.members_table.verticalHeader().setVisible(False)
        self.members_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.members_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.members_table.setAlternatingRowColors(True)
        self.members_table.setShowGrid(True)
        self.setup_table_style(self.members_table)
        
        layout.addWidget(self.members_table, stretch=1)
        
        self.content_stack.addWidget(self.members_page)
        
        # Load archived members data
        self.load_archived_members()
    
    def create_shelf_archive_page(self):
        """Create the shelf archive page"""
        self.shelf_page = QWidget()
        self.shelf_page.setStyleSheet("background-color: #f1efe3;")
        
        layout = QVBoxLayout(self.shelf_page)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Search and filter section
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.shelf_search = QLineEdit()
        self.shelf_search.setPlaceholderText("Search archived shelves...")
        self.shelf_search.setFont(QFont("Times New Roman", 12))
        self.shelf_search.setFixedHeight(35)
        self.shelf_search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e8d8bd;
                border-radius: 10px;
                background-color: #fff;
                color: #5e3e1f;
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: #f5f3ed;
            }
        """)
        self.shelf_search.textChanged.connect(self.search_archived_shelves)
        search_layout.addWidget(self.shelf_search)
        
        
        layout.addLayout(search_layout)
       
        self.shelf_table = QTableWidget()
        self.shelf_table.setColumnCount(5)  
        self.shelf_table.setHorizontalHeaderLabels([
           "Date Deleted", "Shelf ID", "Shelf Name", "Librarian ID", "Select"
        ])

        header = self.shelf_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  
        header.setSectionResizeMode(1, QHeaderView.Stretch) 
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.shelf_table.setColumnWidth(3, 150)      
        self.shelf_table.setColumnWidth(2, 150) 

        self.shelf_table.verticalHeader().setVisible(False)
        self.shelf_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.shelf_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.shelf_table.setAlternatingRowColors(True)
        self.shelf_table.setShowGrid(True)
        self.setup_table_style(self.shelf_table)
        
        layout.addWidget(self.shelf_table, stretch=1)
        
        self.content_stack.addWidget(self.shelf_page)
        
        # Load archived shelves data
        self.load_archived_shelves()

    def show_books_archive(self):
        """Switch to the books archive view"""
        self.content_stack.setCurrentWidget(self.books_page)
        
        # Reset all buttons to inactive style first
        self.books_btn.setStyleSheet(self.button_base_style)
        self.shelf_btn.setStyleSheet(self.button_base_style)
        self.members_btn.setStyleSheet(self.button_base_style)
        
        # Then set the active button
        self.books_btn.setStyleSheet(self.button_active_style)

    def show_shelf_archive(self):
        """Switch to the shelf archive view"""
        self.content_stack.setCurrentWidget(self.shelf_page)
        
        # Reset all buttons to inactive style first
        self.books_btn.setStyleSheet(self.button_base_style)
        self.shelf_btn.setStyleSheet(self.button_base_style)
        self.members_btn.setStyleSheet(self.button_base_style)
        
        # Then set the active button
        self.shelf_btn.setStyleSheet(self.button_active_style)

    def show_members_archive(self):
        """Switch to the members archive view"""
        self.content_stack.setCurrentWidget(self.members_page)
        
        # Reset all buttons to inactive style first
        self.books_btn.setStyleSheet(self.button_base_style)
        self.shelf_btn.setStyleSheet(self.button_base_style)
        self.members_btn.setStyleSheet(self.button_base_style)
        
        # Then set the active button
        self.members_btn.setStyleSheet(self.button_active_style)
    
    def load_archived_books(self):
        """Load archived books from database"""
        try:
            archived_books = self.db_seeder.archiveTable("Book", self.librarian_id or 1)
            book_authors = self.db_seeder.archiveTable("BookAuthor", self.librarian_id or 1)
            book_genres = self.db_seeder.archiveTable("Book_Genre", self.librarian_id or 1)
                    
            self.display_archived_books(archived_books, book_authors, book_genres)
        
        except Exception as e:
            print(f"Error loading archived books: {e}")
    
    def load_archived_members(self):
        """Load archived members from database"""
        try:
            #dito ilalagay yung db lo
            archived_members = self.db_seeder.archiveTable("Member", self.librarian_id or 1)
            
            self.display_archived_members(archived_members)
        except Exception as e:
            print(f"Error loading archived members: {e}")
    
    def load_archived_shelves(self):
        """Load archived shelves from database"""
        try:
            #dito ilalagay yung db lo
            archived_shelves = self.db_seeder.archiveTable("BookShelf", self.librarian_id or 1)
            
            self.display_archived_shelves(archived_shelves)
        except Exception as e:
            print(f"Error loading archived shelves: {e}")
    
    def display_archived_books(self, books, book_authors, book_genres):
        """Display archived books in the table"""
        from PySide6.QtWidgets import QCheckBox
        
        self.books_table.setRowCount(len(books))
        
        for row, book in enumerate(books):
            book_code = book.get('BookCode', '')
            
            # Get all authors for this book
            authors = [a.get('bookAuthor', '') for a in book_authors if a.get('BookCode') == book_code]
            author_text = ', '.join(authors) if authors else 'Unknown Author'

            # Get all genres for this book
            genres = [g.get('Genre', '') for g in book_genres if g.get('BookCode') == book_code]
            genre_text = ', '.join(genres) if genres else 'Unknown Genre'
            
            # Book details columns
            self.books_table.setItem(row, 0, QTableWidgetItem(str(book.get('isDeleted', 'N/A'))))
            self.books_table.setItem(row, 1, QTableWidgetItem(str(book_code)))
            self.books_table.setItem(row, 2, QTableWidgetItem(book.get('BookTitle', 'N/A')))
            self.books_table.setItem(row, 3, QTableWidgetItem(author_text))
            self.books_table.setItem(row, 4, QTableWidgetItem(genre_text))
            self.books_table.setItem(row, 5, QTableWidgetItem(str(book.get('ISBN', 'N/A'))))
            
            # Create centered copies item
            copies_item = QTableWidgetItem(str(book.get('BookTotalCopies', 'N/A')))
            copies_item.setTextAlignment(Qt.AlignCenter)
            self.books_table.setItem(row, 6, copies_item)
            
            # Create centered shelf item - properly handle BookShelf column
            shelf_text = book.get('BookShelf', 'No Shelf')
            if shelf_text is None or shelf_text == '':
                shelf_text = 'No Shelf'
            shelf_item = QTableWidgetItem(str(shelf_text))
            shelf_item.setTextAlignment(Qt.AlignCenter)
            self.books_table.setItem(row, 7, shelf_item)

            # Checkbox for selection with checkmark icon
            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox {
                    margin-left: 12px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:checked {
                    background-color: white;
                    border: 2px solid #5e3e1f;
                    border-radius: 4px;
                    image: url('assets/check.png');  
                }
                QCheckBox::indicator:unchecked {
                    background-color: white;
                    border: 2px solid #d0d0d0;
                    border-radius: 4px;
                }
            """)

            checkbox.toggled.connect(lambda checked, r=row: self.on_book_checkbox_toggled(checked, r))
            
            # Center the checkbox
            checkbox_widget = QWidget()
            checkbox_widget.setStyleSheet("background-color: transparent;")
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            
            self.books_table.setCellWidget(row, 8, checkbox_widget)
            self.books_table.setRowHeight(row, 40)
    
    def display_archived_members(self, members):
        """Display archived members in the table"""
        from PySide6.QtWidgets import QCheckBox
        
        self.members_table.setRowCount(len(members))
        
        for row, member in enumerate(members):
            # Map database columns to display columns
            # Database columns: MemberID, MemberLN, MemberMI, MemberFN, MemberContact, CreatedAt, isDeleted, LibrarianID
            
            # Member details with correct column mapping
            self.members_table.setItem(row, 0, QTableWidgetItem(str(member.get('isDeleted', 'N/A'))))
            self.members_table.setItem(row, 1, QTableWidgetItem(str(member.get('MemberID', 'N/A'))))
            self.members_table.setItem(row, 2, QTableWidgetItem(member.get('MemberFN', 'N/A')))
            self.members_table.setItem(row, 3, QTableWidgetItem(member.get('MemberMI', 'N/A') or 'N/A'))
            self.members_table.setItem(row, 4, QTableWidgetItem(member.get('MemberLN', 'N/A')))
            self.members_table.setItem(row, 5, QTableWidgetItem(str(member.get('MemberContact', 'N/A'))))
            
            # Checkbox for selection
            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox {
                    margin-left: 12px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:checked {
                    background-color: white;
                    border: 2px solid #5e3e1f;
                    border-radius: 4px;
                    image: url('assets/check.png');  
                }
                QCheckBox::indicator:unchecked {
                    background-color: white;
                    border: 2px solid #d0d0d0;
                    border-radius: 4px;
                }
            """)

            checkbox.toggled.connect(lambda checked, r=row: self.on_member_checkbox_toggled(checked, r))
            
            # Center the checkbox
            checkbox_widget = QWidget()
            checkbox_widget.setStyleSheet("background-color: transparent;")
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            
            self.members_table.setCellWidget(row, 6, checkbox_widget)
            self.members_table.setRowHeight(row, 40)
    
    def display_archived_shelves(self, shelves):
        """Display archived shelves in the table"""
        from PySide6.QtWidgets import QCheckBox
        
        self.shelf_table.setRowCount(len(shelves))
        
        for row, shelf in enumerate(shelves):
            # Map database columns to display columns
            # Database columns would be: ShelfId, LibrarianID if table had isDeleted column
           
            #is Deleted
            id_item = QTableWidgetItem(str(shelf.get('isDeleted', 'N/A')))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.shelf_table.setItem(row, 0, id_item)
            # Shelf ID 
            id_item = QTableWidgetItem(str(shelf.get('ShelfId', 'N/A')))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.shelf_table.setItem(row, 1, id_item)
            
            # Shelf Name
            id_item = QTableWidgetItem(str(shelf.get('ShelfName', 'N/A')))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.shelf_table.setItem(row, 2, id_item)
            
            # Librarian ID 
            librarian_item = QTableWidgetItem(str(shelf.get('LibrarianID', 'N/A')))
            librarian_item.setTextAlignment(Qt.AlignCenter)
            self.shelf_table.setItem(row, 3, librarian_item)
            
            # Checkbox for selection
            checkbox = QCheckBox()
            checkbox.setStyleSheet("""
                QCheckBox {
                    margin-left: 12px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
                QCheckBox::indicator:checked {
                    background-color: white;
                    border: 2px solid #5e3e1f;
                    border-radius: 4px;
                    image: url('assets/check.png');  
                }
                QCheckBox::indicator:unchecked {
                    background-color: white;
                    border: 2px solid #d0d0d0;
                    border-radius: 4px;
                }
            """)

            checkbox.toggled.connect(lambda checked, r=row: self.on_shelf_checkbox_toggled(checked, r))
            
            # Center the checkbox
            checkbox_widget = QWidget()
            checkbox_widget.setStyleSheet("background-color: transparent;")
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            
            self.shelf_table.setCellWidget(row, 4, checkbox_widget)
            self.shelf_table.setRowHeight(row, 40)
    
    def search_archived_books(self):
        """Search archived books based on input"""
        search_text = self.books_search.text().strip()
        if not search_text:
            self.load_archived_books()
            return
            
        try:
            # Use database search for archived books
            print(f"🔍 Searching archived books for: '{search_text}'")
            archived_books = self.db_seeder.search_archived_records("Book", search_text, self.librarian_id or 1)
            
            # Also get authors and genres for the filtered books
            book_authors = self.db_seeder.archiveTable("BookAuthor", self.librarian_id or 1)
            book_genres = self.db_seeder.archiveTable("Book_Genre", self.librarian_id or 1)
            
            self.display_archived_books(archived_books, book_authors, book_genres)
            print(f"✓ Displayed {len(archived_books)} filtered archived books")
            
        except Exception as e:
            print(f"Error searching archived books: {e}")
            self.load_archived_books()  # Fallback to showing all
    
    def search_archived_members(self):
        """Search archived members based on input"""
        search_text = self.members_search.text().strip()
        if not search_text:
            self.load_archived_members()
            return
            
        try:
            # Use database search for archived members
            print(f"🔍 Searching archived members for: '{search_text}'")
            archived_members = self.db_seeder.search_archived_records("Member", search_text, self.librarian_id or 1)
            
            self.display_archived_members(archived_members)
            print(f"✓ Displayed {len(archived_members)} filtered archived members")
            
        except Exception as e:
            print(f"Error searching archived members: {e}")
            self.load_archived_members()  # Fallback to showing all
    
    def search_archived_shelves(self):
        """Search archived shelves based on input"""
        search_text = self.shelf_search.text().strip()
        if not search_text:
            self.load_archived_shelves()
            return
            
        try:
            # Use database search for archived shelves
            print(f"🔍 Searching archived shelves for: '{search_text}'")
            archived_shelves = self.db_seeder.search_archived_records("BookShelf", search_text, self.librarian_id or 1)
            
            self.display_archived_shelves(archived_shelves)
            print(f"✓ Displayed {len(archived_shelves)} filtered archived shelves")
            
        except Exception as e:
            print(f"Error searching archived shelves: {e}")
            self.load_archived_shelves()  # Fallback to showing all

    def setup_table_style(self, table):
        """Apply styling to table widget"""
        table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border: 1px solid #e8d8bd;
                border-radius: 8px;
                gridline-color: #e8d8bd;
                font-family: 'Times New Roman';
                font-size: 14px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #f5f3ed;
                color: #5e3e1f;
            }
            QHeaderView::section {
                background-color: #5e3e1f;
                color: white;
                font-weight: bold;
                font-family: 'Times New Roman';
                font-size: 16px;
                padding: 10px;
                border: none;
                border-right: 1px solid #5e3e1f;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """)
    
    def on_book_checkbox_toggled(self, checked, row):
        """Handle book checkbox toggle"""
        if checked:
            # Get book details for confirmation
            book_code = self.books_table.item(row, 1).text()
            book_title = self.books_table.item(row, 2).text()
            
            # Show confirmation dialog
            confirm = QMessageBox.question(
                self, 
                "Confirm Restore",
                f"Are you sure you want to restore the book:\n\n{book_code} - {book_title}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.db_seeder.restoreArchive("Book", book_code, self.librarian_id or 1)
                QMessageBox.information(self, "Success", f"Book '{book_title}' restored successfully.")
                self.load_archived_books()  # Reload the list
            else:
                # Uncheck the checkbox if user cancelled
                checkbox_widget = self.books_table.cellWidget(row, 8)
                checkbox = checkbox_widget.findChild(QCheckBox)
                checkbox.setChecked(False)

    def on_member_checkbox_toggled(self, checked, row):
        """Handle member checkbox toggle"""
        if checked:
            # Get member details for confirmation
            member_id = self.members_table.item(row, 1).text()
            first_name = self.members_table.item(row, 2).text()
            last_name = self.members_table.item(row, 4).text()
            
            # Show confirmation dialog
            confirm = QMessageBox.question(
                self, 
                "Confirm Restore",
                f"Are you sure you want to restore the member:\n\n{member_id} - {first_name} {last_name}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.db_seeder.restoreArchive("Member", member_id, self.librarian_id or 1)
                QMessageBox.information(self, "Success", f"Member '{first_name} {last_name}' restored successfully.")
                self.load_archived_members()  # Reload the list
            else:
                # Uncheck the checkbox if user cancelled
                checkbox_widget = self.members_table.cellWidget(row, 6)
                checkbox = checkbox_widget.findChild(QCheckBox)
                checkbox.setChecked(False)

    def on_shelf_checkbox_toggled(self, checked, row):
        """Handle shelf checkbox toggle"""
        if checked:
            # Get shelf details for confirmation
            shelf_id = self.shelf_table.item(row, 1).text()
            
            # Show confirmation dialog
            confirm = QMessageBox.question(
                self, 
                "Confirm Restore",
                f"Are you sure you want to restore the shelf:\n\nShelf ID: {shelf_id}?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if confirm == QMessageBox.Yes:
                self.db_seeder.restoreArchive("BookShelf", shelf_id, self.librarian_id or 1)
                QMessageBox.information(self, "Success", f"Shelf '{shelf_id}' restored successfully.")
                self.load_archived_shelves()  # Reload the list
            else:
                # Uncheck the checkbox if user cancelled
                checkbox_widget = self.shelf_table.cellWidget(row, 4)
                checkbox = checkbox_widget.findChild(QCheckBox)
                checkbox.setChecked(False)

# Run the application if executed directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Initialize navigation manager
    nav_manager.initialize(app)
    
    window = ArchiveManager()
    window.showMaximized()
    nav_manager._current_window = window  
    
    sys.exit(app.exec())