import sys
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QTimer
from PySide6.QtGui import QFont, QIcon, QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QLineEdit, QScrollArea, QGridLayout,
    QTabWidget, QTextEdit, QMessageBox, QFormLayout
)

#for the navbar to automatically open
class HoverButton(QPushButton):
    def __init__(self, parent_sidebar):
        super().__init__()
        self.parent_sidebar = parent_sidebar
    
    def enterEvent(self, event):
        """Called when mouse enters the button"""
        self.parent_sidebar.expand_sidebar() #to trigger sidebar
        super().enterEvent(event) #call the event

class NavigationArea(QWidget):
    def __init__(self, parent_sidebar):
        super().__init__()
        self.parent_sidebar = parent_sidebar
        self.setMouseTracking(True)  # Enable mouse tracking
    
    def enterEvent(self, event):
        """Called when mouse enters the navigation area"""
        self.parent_sidebar.expand_sidebar()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Called when mouse leaves the navigation area"""
        self.parent_sidebar.start_collapse_timer()
        super().leaveEvent(event)

class BookEditView(QWidget):
    def __init__(self, book_data, parent_window):
        super().__init__()
        self.book_data = book_data #store the book_data(title, author...)
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
                font-size: 32px;
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
                border-radius: 15px;
                border: 2px solid #dbcfc1;
            }
        """)
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)
        
        # Book details form
        self.title_input = QLineEdit(self.book_data['title'])
        self.title_input.setStyleSheet(self.get_input_style())
        
        self.author_input = QLineEdit(self.book_data['author'])
        self.author_input.setStyleSheet(self.get_input_style())
        
        self.isbn_input = QLineEdit(self.book_data.get('isbn', 'N/A'))
        self.isbn_input.setStyleSheet(self.get_input_style())
        
        self.description_input = QTextEdit(self.book_data.get('description', 'No description available'))
        self.description_input.setMaximumHeight(150)
        self.description_input.setStyleSheet("""
            QTextEdit {
                color: #5C4033;
                font-size: 16px;
                padding: 10px;
                background-color: white;
                border: 2px solid #dbcfc1;
                border-radius: 8px;
            }
            QTextEdit:focus {
                border-color: #5C4033;
            }
        """)
        
        # JAS PADAGDAG HERE NG UHMMM NALIMUTAN KO MWHEHEHE PERO NASA PAPER YUNG SHELF ROW SOMETHING
        form_layout.addRow(self.create_label("Title:"), self.title_input)
        form_layout.addRow(self.create_label("Author:"), self.author_input)
        form_layout.addRow(self.create_label("ISBN:"), self.isbn_input)
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
                border-radius: 10px;
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
                border-radius: 10px;
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
    
    def get_input_style(self):
        return """
            QLineEdit {
                color: #5C4033;
                font-size: 16px;
                padding: 10px;
                background-color: white;
                border: 2px solid #dbcfc1;
                border-radius: 8px;
            }
            QLineEdit:focus {
                border-color: #5C4033;
            }
        """
    
    def save_changes(self):
        # Update book data
        self.book_data['title'] = self.title_input.text()
        self.book_data['author'] = self.author_input.text()
        self.book_data['isbn'] = self.isbn_input.text()
        self.book_data['description'] = self.description_input.toPlainText()
        
        # Show confirmation
        msg = QMessageBox()
        msg.setWindowTitle("Success")
        msg.setText(f"Book '{self.book_data['title']}' has been updated successfully!")
        msg.setIcon(QMessageBox.Information)
        msg.exec()
        
        # Go back to main books view
        self.parent_window.show_books_view()
    
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

class CollapsibleSidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.setFixedSize(1300, 700)
        
        # Initialize books data PYTHON LIST!
        self.books_data = [
            {"image": "assets/book1.png", "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "978-0-7432-7356-5", "description": "A classic American novel set in the 1920s."},
            {"image": "assets/book2.png", "title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "978-0-06-112008-4", "description": "A gripping tale of racial injustice and childhood in the American South."},
            {"image": "assets/book3.png", "title": "1984", "author": "George Orwell", "isbn": "978-0-452-28423-4", "description": "A dystopian social science fiction novel and cautionary tale."},
            {"image": "assets/book4.png", "title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "978-0-14-143951-8", "description": "A romantic novel of manners written by Jane Austen."},
            {"image": "assets/book5.png", "title": "The Catcher in the Rye", "author": "J.D. Salinger", "isbn": "978-0-316-76948-0", "description": "A controversial novel originally published for adults."},
            {"image": "assets/book6.png", "title": "Lord of the Flies", "author": "William Golding", "isbn": "978-0-571-05686-2", "description": "A 1954 novel about a group of British boys stuck on an uninhabited island."},
            {"image": "assets/book7.png", "title": "Animal Farm", "author": "George Orwell", "isbn": "978-0-452-28424-1", "description": "An allegorical novella reflecting events leading up to the Russian Revolution."},
            {"image": "assets/book8.png", "title": "Brave New World", "author": "Aldous Huxley", "isbn": "978-0-06-085052-4", "description": "A dystopian novel set in a futuristic World State."},
            {"image": "assets/book9.png", "title": "The Hobbit", "author": "J.R.R. Tolkien", "isbn": "978-0-547-92822-7", "description": "A children's fantasy novel about the adventure of Bilbo Baggins."},
            {"image": "assets/book10.png", "title": "Fahrenheit 451", "author": "Ray Bradbury", "isbn": "978-1-4516-7331-9", "description": "A dystopian novel about a future where books are outlawed."},
            {"image": "assets/book11.png", "title": "Moby Dick", "author": "Herman Melville", "isbn": "978-0-14-243724-7", "description": "The narrative of Captain Ahab's obsessive quest for revenge."},
            {"image": "assets/book12.png", "title": "War and Peace", "author": "Leo Tolstoy", "isbn": "978-0-14-044793-4", "description": "A novel that chronicles the French invasion of Russia."},
            {"image": "assets/book13.png", "title": "The Odyssey", "author": "Homer", "isbn": "978-0-14-044911-2", "description": "An ancient Greek epic poem attributed to Homer."},
            {"image": "assets/book14.png", "title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "isbn": "978-0-14-044913-6", "description": "A psychological novel focusing on the mental anguish of Raskolnikov."},
            {"image": "assets/book15.png", "title": "Jane Eyre", "author": "Charlotte Brontë", "isbn": "978-0-14-144114-6", "description": "A bildungsroman following the experiences of its eponymous heroine."}
        ]
        
        # Main layout
        main_layout = QHBoxLayout(self)

        # Sidebar
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(60)
        self.sidebar_widget.setStyleSheet(
            """
            background-color: #dbcfc1;
            border-radius: 10px;
            """
        )
        
        # Sidebar full layout
        full_sidebar_layout = QVBoxLayout(self.sidebar_widget)
        full_sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Toggle button at the top
        self.toggle_button = QPushButton("< >")
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.toggle_button.setFixedHeight(40)
        full_sidebar_layout.addWidget(self.toggle_button, alignment=Qt.AlignTop)

        # Spacer above icons (top empty space)
        full_sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Create navigation area widget that will detect mouse enter/leave
        self.nav_area = NavigationArea(self)
        self.nav_area.setStyleSheet("background-color: transparent;")
        
        # Navigation buttons layout (centered) - now inside nav_area
        self.sidebar_layout = QVBoxLayout(self.nav_area)
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        self.sidebar_layout.setContentsMargins(5, 10, 5, 10)  # Add some padding

        self.buttons = []

        # Navigation items: (icon, label)
        nav_items = [
            ("assets/dashboard.png", "    Dashboard"),
            ("assets/books.png", "    Books"),
            ("assets/members.png", "    Members"),
            ("assets/settings.png", "    Settings")
        ]

        for icon_path, label in nav_items:
            btn = HoverButton(self)  # Use custom HoverButton
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(30, 30))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setMinimumHeight(40)
            btn.label_text = label
            btn.setText("")  # Start with no text

            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding-left: 10px;
                    color: #5C4033;
                    border: none;
                    font-size: 18px;
                }
                QPushButton:hover {
                    background-color: #E0E0E0;
                }
            """)

            btn.setLayoutDirection(Qt.LeftToRight)
            self.sidebar_layout.addWidget(btn)
            self.buttons.append(btn)

        # Add the navigation area to the main sidebar layout
        full_sidebar_layout.addWidget(self.nav_area)

        # Spacer below icons (bottom empty space)
        full_sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Main content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f1efe3;")
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main books view
        self.main_books_view = self.create_main_books_view()
        self.content_layout.addWidget(self.main_books_view)
        
        # Keep track of current view
        self.current_view = "books"

        # Combine sidebar and content area
        main_layout.addWidget(self.sidebar_widget)
        main_layout.addWidget(self.content_area)

        # Animation setup
        self.expanded = False
        self.manually_expanded = False  # Track if expanded by toggle button
        self.animation = QPropertyAnimation(self.sidebar_widget, b"minimumWidth")
        self.animation.setDuration(250)
        
        # Timer for delayed collapse (prevents flickering when moving mouse quickly)
        self.collapse_timer = QTimer()
        self.collapse_timer.setSingleShot(True)
        self.collapse_timer.timeout.connect(self.collapse_sidebar_hover)

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
        self.search_bar.setPlaceholderText("Search books, pati ba author? wag na")
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
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.search_button)
        
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
        search_text = self.search_bar.text().strip()
        if search_text:
            print(f"Searching for: {search_text}")
            # Here you would implement your actual search functionality
        else:
            print("Please enter a search term")

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
        card_widget = QPushButton()  # Changed to QPushButton to make it clickable
        card_widget.setFixedSize(180, 240)
        card_widget.clicked.connect(lambda: self.open_book_edit(book_data))
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
        
        # Try to load image or show placeholder
        try:
            pixmap = QIcon(book_data["image"]).pixmap(116, 156)
            book_cover.setPixmap(pixmap)
            book_cover.setScaledContents(True)
        except:
            book_cover.setText("📚")
            book_cover.setStyleSheet("""
                QLabel {
                    background-color: #dbcfc1;
                    border-radius: 8px;
                    border: 2px solid #5C4033;
                    font-size: 40px;
                }
            """)
        
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
        author_label = QLabel(book_data["author"])
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
        self.populate_books()

    def toggle_sidebar(self):
        """Manual toggle function using the <> button"""
        self.manually_expanded = not self.manually_expanded
        self.collapse_timer.stop()
        
        if self.manually_expanded:
            self.expand_sidebar_manual()
        else:
            self.collapse_sidebar_manual()

    def expand_sidebar_manual(self):
        """Expand the sidebar manually (via toggle button)"""
        self.expanded = True
        self.animation.setStartValue(self.sidebar_widget.width())
        self.animation.setEndValue(180)
        for btn in self.buttons:
            btn.setText(f"  {btn.label_text}")
        self.animation.start()

    def collapse_sidebar_manual(self):
        """Collapse the sidebar manually (via toggle button)"""
        self.expanded = False
        self.animation.setStartValue(self.sidebar_widget.width())
        self.animation.setEndValue(60)
        for btn in self.buttons:
            btn.setText("")
        self.animation.start()

    def expand_sidebar(self):
        """Expand the sidebar on hover (only if not manually expanded)"""
        if not self.manually_expanded and not self.expanded:
            self.expanded = True
            self.collapse_timer.stop()
            self.animation.setStartValue(self.sidebar_widget.width())
            self.animation.setEndValue(180)
            for btn in self.buttons:
                btn.setText(f"  {btn.label_text}")
            self.animation.start()

    def start_collapse_timer(self):
        """Start the collapse timer (only if not manually expanded)"""
        if not self.manually_expanded:
            self.collapse_timer.start(200)

    def collapse_sidebar_hover(self):
        """Collapse the sidebar on hover timeout (only if not manually expanded)"""
        if not self.manually_expanded and self.expanded:
            self.expanded = False
            self.animation.setStartValue(self.sidebar_widget.width())
            self.animation.setEndValue(60)
            for btn in self.buttons:
                btn.setText("")
            self.animation.start()

# Run app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Times New Roman", 10))
    window = CollapsibleSidebar()
    window.show()
    app.exec()