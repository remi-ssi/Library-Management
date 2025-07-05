import sys
from navbar_logic import nav_manager
from .transaction_logic import BorrowBooks

from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QLineEdit, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QStackedWidget, QMainWindow
)
from functools import partial
from .AddTransactionForm import AddTransactionForm  # PARA MA-IMPORT UNG TRANSACTION FORM 
from .PreviewTransactionForm import PreviewTransactionForm # PARA MA-IMPORT UNG PREVIEW NG TRANSACTION
from .HistoryPreviewForm import HistoryTransactionPreviewForm # PARA MA-IMPORT UNG PREVIEW NG HISTORY 
from navigation_sidebar import NavigationSidebar # PARA SA SIDE BAR 

class TransactionCard(QFrame):
    #initialize transaction widget with transaction data and parent system reference
    def __init__(self, transaction, parent_system):
        super().__init__() #call parent class container (QMainWIndow)
        self.transaction = transaction #sstore transaction data
        self.parent_system = parent_system #store references to parent systm for callbbacks/updates
        self.setup_ui() #initialize UI components
        
    def setup_ui(self):
        #create and configure main  window frame
        central_widget = QWidget() #creat central widget that will hold all other widgets
        self.setFixedSize(280, 210)  #fixed window size
        self.setFrameStyle(QFrame.Box) #set frame to show borders
        self.setCentralWidget(central_widget) 
        self.setStyleSheet(""" #applu custom styling using CSS-like syntax
            QFrame {
                background-color: #e8d8bd;
                border-radius: 15px;
                     
            }
            QFrame:hover {
                border-color: #5e3e1f;
                background-color: #5e3e1f;
            }
        """)
        #create vertical box layout for widgets
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        # Book title label
        title_label = QLabel(f"Book: {self.transaction['book_title']}") #create label showing book title from transaction data
        title_label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        title_label.setWordWrap(True) #enable word wrapping for long titles
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #8B4513; background: none; border: none; margin-bottom: 4px;")
        title_label.setFrameStyle(QFrame.NoFrame) #remove frame around label
        layout.addWidget(title_label) # add lable to layout

        # Borrower name label
        borrower_label = QLabel(f"Borrower: {self.transaction['borrower']}") #label showing the borrower name
        borrower_label.setFont(QFont("Times New Roman", 10)) #font properties
        borrower_label.setAlignment(Qt.AlignCenter)
        borrower_label.setStyleSheet("color: #e8d8bd; background: none; border: none; margin-bottom: 8px;")
        borrower_label.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(borrower_label) #add to layout

        # Borrow date label
        date_label = QLabel(f"Date: {self.transaction['date']}") #lable showing the borrow date
        date_label.setFont(QFont("Times New Roman", 10)) #set font 
        date_label.setAlignment(Qt.AlignCenter)
        date_label.setStyleSheet("color: #8B7B6A; background: none; border: none;")
        date_label.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(date_label) #add to layout

        # Due date label (only shown in due date exists)
        if self.transaction.get('due_date'):
            due_label = QLabel(f"Due: {self.transaction['due_date']}") #show the due date
            due_label.setFont(QFont("Times New Roman", 10))
            due_label.setAlignment(Qt.AlignCenter) 
            if self.transaction['action'] == 'Borrowed': #different styling based on transaction status
                due_date = datetime.strptime(self.transaction['due_date'], "%Y-%m-%d")
                today = datetime.now() #get current date
                if due_date < today:
                    #red color for overdue items
                    due_label.setStyleSheet("color: #e74c3c; font-weight: bold; background: none; border: none;")
                else:
                    #green color for borrowed items
                    due_label.setStyleSheet("color: #27ae60; background: none; border: none;")
            else:
                #gray color for returned items
                due_label.setStyleSheet("color: #888; background: none; border: none;")
            due_label.setFrameStyle(QFrame.NoFrame) 
            layout.addWidget(due_label)

        layout.addStretch() # add strechable space in layout
        #only show is transaction is returnd and has a returned date
        if self.transaction['action'] == 'Returned' and self.transaction.get('returned_date'):
            returned_label = QLabel(f"Returned: {self.transaction['returned_date']}")
            returned_label.setFont(QFont("Times New Roman", 10))
            returned_label.setAlignment(Qt.AlignCenter)
            #brown color for return date
            returned_label.setStyleSheet("color: #8B4513; background: none; border: none;")
            layout.addWidget(returned_label)

        layout.addStretch() #add more stretchable space

       # Status indicator at bottom
        if self.transaction['action'] == 'Borrowed':
            #parse due date for comparison
            due_date = datetime.strptime(self.transaction['due_date'], "%Y-%m-%d"), #get due date from transaction
            today = datetime.now() #get time now
            if due_date < today:
                #overdue styling (dark brown, white text)
                status_label = QLabel("Overdue")
                status_label.setStyleSheet("""
                    background-color: #5e3e1f;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 10px;
                """)
            else:
                #normal borrowwed styling
                status_label = QLabel("BORROWED")
                status_label.setStyleSheet("""
                    background-color: #8B4513;
                    color: white;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-weight: bold;
                    font-size: 10px;
                """)
        else:
            #returned styling
            status_label = QLabel("RETURNED")
            status_label.setStyleSheet("""
                background-color: #8B4513;
                color: white;
                padding: 6px 12px;
                border-radius: 15px;
                font-weight: bold;
                font-size: 10px;
            """)
        #center status label and add to layout 
        status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(status_label)

class LibraryTransactionSystem(QMainWindow):
    def __init__(self, librarian_id=None):
        #initialize ethe parent window
        super().__init__()
        self.librarian_id = librarian_id #store librarian id for authorization
        self.borrow_books = BorrowBooks() # Initialize BorrowBooks functionality
        self.setGeometry(100, 100, 1400, 800) #set initialize window position and size
        self.showMaximized() #start window in maximized state
        self.setStyleSheet("background-color: white;") #default background color
        self.transactions = [] ##initialized empty transaction list
        self.setup_ui() #set up UI

        self.setStyleSheet("""
            LibraryTransactionSystem {
                background-color: #f1efe3;
            }
        """)

    def setup_ui(self):
        #create central widget that holds all content
        central_widget = QWidget()
        self.setCentralWidget(central_widget)      
        #main horizontal layout (sidebar + content area)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0,0,0,0) #no margins
        main_layout.setSpacing(0)  #no spacing between widgets

        self.sidebar = NavigationSidebar() # for nav sidebar
        self.sidebar.navigation_clicked.connect( #connect sidebar click signals to nabiagte handler
            lambda item_name: nav_manager.handle_navigation(item_name, self.librarian_id)
        )
        #add sidebar to main layout
        main_layout.addWidget(self.sidebar)
        #create coneten are widget
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f3ed;") #off white background
        main_layout.addWidget(content_widget)
        #vertical layout for content area
        content_layout= QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0,0,0,0) #no margins
        content_layout.setSpacing(0)

        # Header
        header_widget = QWidget()
        header_widget.setFixedHeight(100) #fixed header height
        header_widget.setStyleSheet("background-color: #f5f3ed;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(40, 20, 40, 20) #padding
        header_layout.setSpacing(20) #space between headerr items

        #main title lable
        title_label = QLabel("Books Management")
        title_label.setFont(QFont("Times New Roman", 32, QFont.Bold))
        title_label.setStyleSheet("color: #5e3e1f; margin-right: 20px;") #brown color
        header_layout.addWidget(title_label)
        header_layout.addStretch() #push following items to right
        content_layout.addWidget(header_widget)

        # Navigation
        nav_widget = QWidget()
        nav_widget.setFixedHeight(60) #fixed navbar height
        nav_widget.setStyleSheet("background-color: white; border-bottom: 1px solid #e8d8bd;")
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(80, 10, 80, 10) #horizontal padding
        nav_layout.setSpacing(10) #space between buttons

        #current transaction button
        self.transactions_btn = QPushButton("Current Transactions")
        self.transactions_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.transactions_btn.setFixedSize(180, 40) #fixed button size
        self.transactions_btn.clicked.connect(self.show_transactions_page)
        nav_layout.addWidget(self.transactions_btn)
      
        #transaction history button
        self.history_btn = QPushButton("Transaction History")
        self.history_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        self.history_btn.setFixedSize(180, 40) #fixed button size
        self.history_btn.clicked.connect(self.show_history_page)
        nav_layout.addWidget(self.history_btn)
        content_layout.addWidget(nav_widget)

        #main content area
        # stacted widget for switching between pages
        self.content_stack = QStackedWidget()
        content_layout.addWidget(self.content_stack)
        
        #initialize both pages
        self.create_transactions_page() 
        self.create_history_page() 
        #show  current transaction page by default
        self.show_transactions_page()


        # METHOD TO CREATE TRANSACTION PAGE
    def create_transactions_page(self):
        #create page widget
        self.transactions_page = QWidget()
        self.transactions_page.setStyleSheet("background-color: #f5f3ed;")
        #main vertical layout
        layout = QVBoxLayout(self.transactions_page)
        layout.setContentsMargins(40, 30, 40, 30) #page padding
        layout.setSpacing(20) #space between widget
        
        #search bar layout (horizontal)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0) #no margins

        #search input fields
        self.trans_search_edit = QLineEdit()
        self.trans_search_edit.setPlaceholderText("Search transactions...")
        self.trans_search_edit.setFont(QFont("Times New Roman", 14))
        self.trans_search_edit.setFixedHeight(45) #search bar height
        self.trans_search_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e8d8bd;
                border-radius: 10px;
                background-color: #fff;
                color: #5e3e1f;
                font-family: 'Times New Roman';
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: #f5f3ed;
            }
        """)
        # connect search tects changes to filtering function
        self.trans_search_edit.textChanged.connect(self.search_transactions)
        search_layout.addWidget(self.trans_search_edit)

        #add transaction button
        add_transaction_btn = QPushButton("➕") #plus symbol for adding transcation
        add_transaction_btn.setStyleSheet("""
            QPushButton {
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
        add_transaction_btn.clicked.connect(self.open_add_transaction_form)
        search_layout.addWidget(add_transaction_btn)
        layout.addLayout(search_layout)  #add search bar to main layout

        #for transaction table
        self.trans_table = QTableWidget()
        self.trans_table.setColumnCount(6) #set 6 columns
        self.trans_table.setHorizontalHeaderLabels([
            "Name", "Book Borrowed", "Borrowed Date", "Transaction Type", "Due Date", "" #empty header for action buttons
        ])
        #table configuration
        self.trans_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) #auto-resize
        self.trans_table.verticalHeader().setVisible(False) #hide row numbers
        self.trans_table.setEditTriggers(QTableWidget.NoEditTriggers) #read only
        self.trans_table.setSelectionBehavior(QTableWidget.SelectRows) #full row selection
        self.trans_table.setAlternatingRowColors(False) #no alternating background color of table rows 
        self.trans_table.setShowGrid(True) #show grid lines
        
        layout.addWidget(self.trans_table, stretch=1) #add table layout with stretch factor
        self.setup_table_style(self.trans_table) #apply custom table styling
        self.trans_table.cellDoubleClicked.connect(self.on_transaction_double_click)  # double-click signal to see vie details
        self.content_stack.addWidget(self.transactions_page)# addp page tostacked widget

    # HISTORY PAGE - transaction history view
    def create_history_page(self):
        #create the history page widget
        self.history_page = QWidget()
        self.history_page.setStyleSheet("background-color:#f5f3ed;") #off white background color
        #main vertical layout for the page
        layout = QVBoxLayout(self.history_page)
        layout.setContentsMargins(40, 30, 40, 30) #set page margins
        layout.setSpacing(20) #set spacing between widgets
        #search bar layout (horizontal)
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0) #no margins
        #create search input field
        self.hist_search_edit = QLineEdit()
        self.hist_search_edit.setPlaceholderText("Search history...")
        self.hist_search_edit.setFont(QFont("Times New Roman", 14))
        self.hist_search_edit.setFixedHeight(45)
        self.hist_search_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e8d8bd;
                border-radius: 8px;
                background-color: #fafafa;
                color: #5C4033;
            }
            QLineEdit:focus {
                border-color: #e8d8bd;
                background-color: white;
            }
        """)
        #connect text changes to search filtering
        self.hist_search_edit.textChanged.connect(self.search_history)
        #add search field to layout
        search_layout.addWidget(self.hist_search_edit)
        #add search bar to maintain layout
        layout.addLayout(search_layout)

        #crete history table widget
        self.hist_table = QTableWidget()
        self.hist_table.setColumnCount(6)
        self.hist_table.setHorizontalHeaderLabels([
            "Borrower", "Book Title", "Borrowed Date", "Returned Date", "Due Date", "Action", " "#extra space colum for action
        ])
        #auto resize columns to fit available copies
        self.hist_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.hist_table.verticalHeader().setVisible(False) #hide row headers
        self.hist_table.setEditTriggers(QTableWidget.NoEditTriggers) #read only
        self.hist_table.setSelectionBehavior(QTableWidget.SelectRows) #select entire rows
        self.hist_table.setAlternatingRowColors(False) #disable alternating row colors
        self.hist_table.setShowGrid(True) #show grid lines

        #add table to layout with stretch factor
        layout.addWidget(self.hist_table, stretch=1)
        self.setup_table_style(self.hist_table) #apply custom table styling
        self.hist_table.cellDoubleClicked.connect(self.on_history_double_click)
        self.content_stack.addWidget(self.history_page)  #add page to stacked widget

    #TSWITCH TO TRANSACTION PAGE VIEW
    def show_transactions_page(self):
        #set current page to transaction
        self.content_stack.setCurrentWidget(self.transactions_page)
        # Active button style (transactions)
        self.transactions_btn.setStyleSheet("""
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
        """)
        # Inactive button style (history)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #8B4513;
                font-weight: normal;
                border-radius: 20px;
                border: 2px solid #e8d8bd;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: ##5e3e1f;
                border-color: #8B4513; 
            }
        """)
        #refresh displayed transactions
        self.display_transactions()

    #SWITCH TO HISTORY PAGE VIEW
    def show_history_page(self):
        #set current page to history
        self.content_stack.setCurrentWidget(self.history_page)
        # Active button style (history)
        self.history_btn.setStyleSheet("""
            QPushButton {
                background-color: #8B4513;
                color: white;
                font-weight: bold;
                border-radius: 20px;
                border: 2px solid #8B4513;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5e3e1f;
                border-color: #5e3e1f;
            }
        """)
        # Inactive button style (transactions)
        self.transactions_btn.setStyleSheet("""
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
        """)
        #refresh displayed history
        self.display_history()

    def display_transactions(self, filtered_transactions=None):
         
        # Always fetch all transactions for the current librarian
        self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id) or []
        print("Transaction(Current):", self.transactions)
        #sort transactions by date (newest first)
        self.transactions.sort(key=lambda x: datetime.strptime(x.get('date', '1970-01-01'), "%Y-%m-%d"), reverse=True)

        # Only show transactions where action is "Borrowed"
        transaction_dict = {}
        for trans in self.transactions:
            if trans.get('action') != 'Borrowed':
                continue
            trans_id = trans.get('id') #group books by transaction id
            if trans_id not in transaction_dict:
                #create transcation entry if not exits
                transaction_dict[trans_id]  = {
                    'id': trans_id,
                    'borrower': trans.get('borrower', 'N/A'),
                    'date': trans.get('date', 'N/A'),
                    'due_date':trans.get('due_date', 'N/A'),
                    'action': trans.get('action', 'Borrowed'),
                    'remarks': trans.get('remarks', ''),
                    'books': [] #list to hold all books in this transactions
                }
                #add book to transaction
            transaction_dict[trans_id]['books'].append({
                'title': trans.get('book_title', 'N/A'),
                'quantity':trans.get('quantity', 1) #default to 1 if missing
            })
            #convert to list and sot by date (newwest first)
        all_transactions = sorted (transaction_dict.values(), key=lambda x:datetime.strptime(x['date'], "%Y-%m-%d"), reverse=True)
        #use filtered transactions if provided, otherwise use all
        transactions_to_display = filtered_transactions if filtered_transactions is not None else all_transactions
        #clear exxisting rows
        self.trans_table.setRowCount(0)
        self.trans_table.setRowCount(len(transactions_to_display))

        #populate table with transaction data
        for row, trans in enumerate(transactions_to_display):
            #determine status if borrowed or overdue
            status =  "Borrowed"
            if trans.get('due_date') and trans['due_date'] != 'N/A':
                try:
                    due_date = datetime.strptime(trans['due_date'], "%Y-%m-%d") #get the due date
                    today = datetime.now() #get time now
                    status = "Overdue" if due_date < today else "Borrowed"
                except ValueError as e: #handle error
                    print(f"Invalid due date format for transaction {trans['id']}: {trans['due_date']} - Error: {str(e)}")
                    status = "Borrowed"
            else:
                print(f"Missing due_date for transaction {trans_id}")
                status = "Borrowed"
            #format  book title with quantities 
            book_titles = ", ".join([f"{book['title']} (x{book['quantity']})" for book in trans['books']])
            total_quantity = sum(book['quantity'] for book in trans['books']) #calculate total quantity of all books in transaction
            #prepare values for each column
            values = [
                trans.get('borrower', 'N/A'), #borrower name
                book_titles, #formatted book list
                trans.get('date', 'N/A'), #borrow date
                status, #status (borrowed/overdue)
                trans.get('due_date', 'N/A'), #due date
                str(total_quantity), #total wuantity
                "" #empty colum for action buttons
            ]
            #create ans style table items      
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setForeground(QColor("#5C4033")) #default to brown text
                if col == 3:  # Status column
                    if status == "Overdue":
                        item.setForeground(QColor("#c0392b")) #red for overdue
                    elif status == "Borrowed":
                        item.setForeground(QColor("#27ae60")) #green for borrowed
                self.trans_table.setItem(row, col, item)

            # --- Delete button ---
            delete_btn = QPushButton("Delete")
            delete_btn.setToolTip("Delete Transaction") #hover text
            delete_btn.setFont(QFont("Segoe UI Emoji", 10, QFont.Bold))
            #style delete button
            delete_btn.setStyleSheet("""
                QPushButton {
                    border-radius: 12px;
                    font-size: 10px;
                    color: #c0392b;
                    background: white;
                    font-family: "Segoe UI Emoji", "Times New Roman";
                    font-weight: bold;
                    border: 2px solid #c0392b;
                    padding: 5px 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            #connect click to delete function with transaction data
            delete_btn.clicked.connect(partial(self.delete_transaction, trans))

            # Center the button in the cell
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.addStretch()
            layout.addWidget(delete_btn)
            layout.addStretch() #add space between buttons
            layout.setContentsMargins(0, 0, 0, 0) #no margins
            self.trans_table.setCellWidget(row, 5, container) # add to action column
            self.trans_table.setRowHeight(row, 40) # set row height

    def search_transactions(self):
        #get search term from input field and remove whitespace
        search_term = self.trans_search_edit.text().strip()
        #if emppty search term, show all transactions
        if not search_term:
            self.display_transactions()
            return
        #log search attempt
        print(f"🔍 Searching transactions for: '{search_term}'")
        try:
            # Use database search instead of local search
            search_results = self.db_seeder.search_records("BookTransaction", search_term, self.librarian_id)
            
            # Filter only borrowed transactions for active view
            borrowed_transactions = [t for t in search_results if t.get('Status') == 'Borrowed']
            
            # Group transactions by TransactionID (same format as original)
            transaction_dict = {}
            for trans in borrowed_transactions:
                trans_id = trans.get('TransactionID')
                if trans_id not in transaction_dict:
                    #create transaction entry with basic info
                    transaction_dict[trans_id] = {
                        'id': trans_id,
                        'borrower': trans.get('borrower', 'N/A'),
                        'date': trans.get('BorrowedDate', 'N/A'),
                        'due_date': trans.get('DueDate', 'N/A'),
                        'action': trans.get('Status', 'Borrowed'),
                        'remarks': trans.get('Remarks', ''),
                        'books': [] #will hold all books in this transction
                    }
                transaction_dict[trans_id]['books'].append({
                    'title': trans.get('BookTitle', 'N/A'),
                    'quantity': trans.get('Quantity', 1)
                })
            #convert to list for display
            filtered_transactions = list(transaction_dict.values())
            print(f"✅ Found {len(filtered_transactions)} matching transactions from database")
            #update display with filtered results
            self.display_transactions(filtered_transactions)
            
        except Exception as e:
            print(f"❌ Error searching transactions: {e}")
            # Fallback to local search if database search fails
            self.perform_local_transaction_search(search_term)
            
    def perform_local_transaction_search(self, search_term):
        """Fallback local transaction search method"""
        search_term = search_term.lower()
        #get only borrowed transactions from cached data
        active_transactions = [t for t in self.transactions if t.get('action') == 'Borrowed']
        #group only borrowed transactions b ID (same as display transaction)
        transaction_dict = {}
        for trans in self.transactions:
            if trans.get('action') != 'Borrowed': #skip non borrowed transctions
                continue
            trans_id = trans.get('id')
            if trans_id not in transaction_dict:
                #creae transaction entry with basic info
                transaction_dict[trans_id] = {
                    'id': trans_id,
                    'borrower': trans.get('borrower', 'N/A'),
                    'date': trans.get('date', 'N/A'),
                    'due_date': trans.get('due_date', 'N/A'),
                    'action': trans.get('action', 'Borrowed'),
                    'remarks': trans.get('remarks', ''),
                    'books': [] #holds he books in this transaction
                }
            transaction_dict[trans_id]['books'].append({
                'title': trans.get('book_title', 'N/A'),
                'quantity': trans.get('quantity', 1) #default quantity 1
            })
        #filter transactions where search term matches borower name or book tilte
        filtered_transactions = [
            trans for trans in transaction_dict.values()
            if search_term in trans['borrower'].lower() or 
            any(search_term in book['title'].lower() for book in trans['books']) #match any book title
        ]
        #log local search results
        print(f"📝 Local search found {len(filtered_transactions)} matching transactions")
        self.display_transactions(filtered_transactions) #update with filter results

    #DISPLAY TRANSACTION HISTORY IN THE HISTORY TABLE
    def display_history(self, filtered_history=None):
        #fetch all transactions for current librarian
        self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id) or []
        print("Transactions (History):", self.transactions)
        #csort all transactions by borrow date
        self.transactions.sort(key=lambda x: datetime.strptime(x.get('date', '1970-01-01'), "%Y-%m-%d"), reverse=True)
        #use filtered history if provided otherwise get all returned transactions
        history_to_display = filtered_history if filtered_history is not None else [
            t for t in self.transactions if t.get('action') == 'Returned'
        ]
        #sort history by return date (newest)
        history_to_display.sort(key=lambda x: datetime.strptime(x.get('returned_date', x.get('date', '1970-01-01')), "%Y-%m-%d"),reverse=True)

        self.hist_table.setRowCount(len(history_to_display)) #set table row count to match number of history items
        #populate tbale with history data
        for row, trans in enumerate(history_to_display):
            values = [
                trans.get('borrower', ''), #member name
                trans.get('book_title', ''), #book title
                trans.get('date', 'N/A'), #borrow date
                trans.get('returned_date', 'N/A'), #date returned
                trans.get('due_date', 'N/A'), #due date
                trans.get('action', 'N/A'), # transaction status (Returned)
            ]
            # create and tyle table items for each column
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setForeground(QColor("#5C4033")) #deafult dark brown text
                if col == 4:
                    if value == "Borrowed": #green text color fo borrowed
                        item.setForeground(QColor("#27ae60"))
                    else: #brown for returned
                        item.setForeground(QColor("#8B4513"))
                self.hist_table.setItem(row, col, item)

            # Delete button on the Transaction History
            delete_btn = QPushButton("Delete")
            delete_btn.setToolTip("Delete Transaction Historty") #hover text
            delete_btn.setFont(QFont("Times New Roman", 10, QFont.Bold))
            delete_btn.setStyleSheet("""
                QPushButton {
                    border-radius: 12px;
                    font-size: 10px;
                    color: #c0392b;
                    background: white;
                    font-family: "Segoe UI Emoji", "Times New Roman";
                    font-weight: bold;
                    border: 2px solid #c0392b;
                    padding:5px 10px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                    color: white;
                }
            """)
            #connect click to delete function with transaction data
            delete_btn.clicked.connect(partial(self.delete_transaction, trans))

            # Center the button using layout
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.addStretch() #add space after button
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch() #add space after button
            actions_layout.setContentsMargins(0, 0, 0, 0)

            #add delete button to last column 
            self.hist_table.setCellWidget(row, 5, actions_widget)
            self.hist_table.setRowHeight(row, 40) #set fixed row height 

    #SEARCH TRANSACTION HISTORY BASED ON USER INPUT
    def search_history(self):
        #get search term from input field and convert to lowercase
        search_term = self.hist_search_edit.text().lower()
        #if search term is emty, show all history
        if not search_term:
            self.display_history()
        else:
            #filter transactions that match search term in any field
            filtered_history = [
        trans for trans in self.transactions
        if (trans.get('action') == 'Returned' and  # Only returned transactions
            (search_term in trans.get('book_title', '').lower() or  # Search book title
             search_term in trans.get('borrower', '').lower() or  # Search borrower name
             search_term in trans.get('returned_date', '').lower() or  # Search returned date
             search_term in trans.get('action', '').lower()))  # Search action type
    ]
            #displayed filtered results
            self.display_history(filtered_history)

    #REFRESH BOTH TRANSACTION AND HISTORY DISPLAYS WITH FRESH DATA
    def refresh_transaction_displays(self):
        """Refresh both transaction and history displays"""
        try:
            print("🔄 Refreshing transaction displays...")
            # Fetch fresh data from database
            self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id)
            # Update both displays
            self.display_transactions()
            self.display_history()
            print("✅ Transaction displays refreshed successfully")
        except Exception as e:
            print(f"❌ Error refreshing displays: {e}")
            QMessageBox.warning(self, "Refresh Error", f"Failed to refresh transaction displays: {str(e)}")

    #OPEN DIALOG TO ADD NEW TRANSACTION
    def open_add_transaction_form(self):
        #get available books from database
        books = self.borrow_books.fetch_books(self.librarian_id)
        if not books: #if no books available, show error message
            QMessageBox.critical(self, "Error", "No books available. Please add books to the database.")
            return
        
        dialog = AddTransactionForm(librarian_id=self.librarian_id, parent=self)
        result = dialog.exec()
        
        # If dialog was accepted, it means transaction was successfully added
        # The AddTransactionForm will have already called refresh_transaction_displays via parent notification
        if result == QDialog.Accepted:
            print("✅ Transaction added successfully and displays refreshed automatically")

    #OPEN DIALOG TO VIEW/EDIT A TRANSACTION
    def open_edit_transaction(self, selected_transaction):
        #get transaction id from selected transaction
        transaction_id = selected_transaction.get('id')
        if not transaction_id:
            print("Error: Missing TransactionID")
            QMessageBox.warning(self, "Error", "Invalid transactionID")
            return
        
        # Aggregate all transaction details for this TransactionID
        related_transactions = [t for t in self.transactions if t['id'] == transaction_id]
        #prepare book list for the transaction
        books = [
            {'title': t['book_title'], 'quantity': t['quantity']}
            for t in related_transactions
        ]

        # Create the transaction dictionary for PreviewTransactionForm
        preview_transaction = {
            'id': transaction_id,
            'borrower': selected_transaction.get('borrower', 'N/A'),
            'date': selected_transaction.get('date', 'N/A'),
            'action': selected_transaction.get('action', 'Borrowed'),
            'due_date': selected_transaction.get('due_date', 'N/A'),
            'returned_date': selected_transaction.get('returned_date', ''),
            'remarks': selected_transaction.get('remarks', ''),
            'books': books
        }

        # Debug: Print the transaction being passed
        print("Opening NewPreviewTransactionForm with transaction:", preview_transaction)

        # Open the PreviewTransactionForm
        dialog = PreviewTransactionForm(preview_transaction, parent=self)
        if dialog.exec():
            updated_transaction = dialog.get_transaction()
            
            # If the transaction is marked as Returned, update the database
            if updated_transaction['action'] == 'Returned':
                try:
                    #update databse with returned status
                    success = self.borrow_books.return_book(
                        transaction_id=updated_transaction['id'],
                        librarian_id=self.librarian_id,
                        returned_date=updated_transaction['returned_date'],
                        remarks=updated_transaction.get('remarks', '')
                    )
                    if success:
                        # Refresh transactions and history
                        self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id) or []
                        self.display_transactions()
                        self.display_history()
                    else: #error handling
                        QMessageBox.critical(self, "Error", "Failed to update transaction status.")
                except Exception as e: #show error from databse if any
                    QMessageBox.critical(self, "Database Error", f"Failed to return transaction: {str(e)}")

    #HANDLE DOUBLE-CLICK EVENT ON TRANSACTION TABLE ROWS
    def on_transaction_double_click(self, row, column):
        if column == 5:  # Skip if clicking on delete button column
            return
        
        # Get the current filtered transactions (same as display_transactions uses)
        search_term = self.trans_search_edit.text().lower()
        transaction_dict = {}
        for trans in self.transactions:
            if trans.get('action') != 'Borrowed': #skip returned transactions
                continue

            #group transactions by id and collect book details
            trans_id = trans.get('id')
            if trans_id not in transaction_dict:
                transaction_dict[trans_id] = {
                    'id': trans_id,
                    'borrower': trans.get('borrower', 'N/A'),
                    'date': trans.get('date', 'N/A'),
                    'due_date': trans.get('due_date', 'N/A'),
                    'action': trans.get('action', 'Borrowed'),
                    'remarks': trans.get('remarks', ''),
                    'books': [] #list to hold all books in this transactions
                }
            #add book details to the transaction
            transaction_dict[trans_id]['books'].append ({
                'title': trans.get('book_title', 'N/A'),
                'quantity': trans.get('quantity', 1)
            })
            #conert dictionary values to list
        active_transactions = list(transaction_dict.values())
        
        #apply search filter if search terms exists
        if search_term:
            filtered_transactions = [
                trans for trans in active_transactions
                if search_term in trans['borrower'].lower() or #match borrower name 
                    any(search_term in book['title'].lower() for book in trans['books']) #match any book title
            ]
        else:
            filtered_transactions = active_transactions
            #validate row index
        if row >= len(filtered_transactions):
            print("Error: row index out of range")
            QMessageBox.critical(self, "Error", "Invalid transaction selected.")
            return
        #get the selected transactions and open edit dialog
        selected_transaction = filtered_transactions[row]
        print(f"Open selected transaction:", selected_transaction)
        self.open_edit_transaction(selected_transaction)


    #  MARK A TRANSACTION AS RETURNED AND OPEN EDIT DIALOG
    def return_transaction(self, transaction):
        #show confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Confirm Return",
            f"Are you sure you want to mark transaction #{transaction['id']} as returned?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                #update transaction status in database
                success = self.borrow_books.return_book (
                    transaction_id = transaction['id'],
                    librarian_id = self.librarian_id,
                    returned_date=datetime.now().strftime("%Y-%m-%d") #cutrrent date
                )
                if success:
                    #refresh data id update was successful
                    self.transactions= self.borrow_books.fetch_all_transactions(self.librarian_id)
                    self.display_transactions()
                    self.display_history()
            except Exception as e:#show error message if update fails
                QMessageBox.critical(self, "Database Error", f"Failed to return transaction: {str(e)}")

    #PERMANENTLY DELTE A TRANSACTION FROM THE DATABASE
    def delete_transaction(self, transaction):
        #show confirmation dialog
        reply = QMessageBox.question(
            self, 
            "Confirm Permanent Delete", 
            f"Are you sure you want to permanently delete transaction #{transaction['id']}?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )

        if reply == QMessageBox.Yes: #if user chose yes in the confirmation dialog
            try:
                #delete transaction from databse
                self.borrow_books.db_seeder.delete_table(tableName="BookTransaction", column="TransactionID", value=transaction['id'] )
                #show success message
                QMessageBox.information(self, "Success", f"Transaction {transaction} deleted successfully!")
                #refresh data
                self.transactions = self.borrow_books.fetch_all_transactions(self.librarian_id)
                self.display_transactions()
                self.display_history()
                
            except Exception as e: #show error message if deletion fails
                QMessageBox.critical(self, "Database Error", f"Failed to delete transaction: {str(e)}")
   
    # STYLING FOR TABLE WIDGETS
    def setup_table_style(self, table):
        table.setStyleSheet("""
            QTableWidget { 
                background-color: white;
                border: 1px solid #e8d8bd-;
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
                color: White;
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

    #HANDLE DOUBLE CLICK EVENTS ON HISTORY TABLE ROWS
    def on_history_double_click(self, row, column):
        if column == 5:  # Skip if clicking on delete button column
            return
        # Use the same data as display_history
        search_term = self.hist_search_edit.text().lower()
        #filter for returned transactions only
        history_transactions = [t for t in self.transactions if t.get('action') == 'Returned']
        #apply search filter if term exists
        if search_term:
            history_transactions = [
                trans for trans in history_transactions
                if (search_term in trans.get('book_title', '').lower() or #search book title
                    search_term in trans.get('borrower', '').lower() or #search borrower
                    search_term in trans.get('returned_date', '').lower() or #search return date
                    search_term in trans.get('action', '').lower()) #search action type
            ]
        # sort transactions by return date (newest first), fallback to borrow date
        sorted_transactions = sorted(
            history_transactions,
            key=lambda x: datetime.strptime(x.get('returned_date', x.get('date', '1970-01-01')), "%Y-%m-%d"),
            reverse=True
        )
        #validate row index
        if row >= len(sorted_transactions):
            print("Error: row index out of range")
            QMessageBox.critical(self, "Error", "Invalid transaction selected.")
            return
        #get selected transaction and open preview dialog
        transaction = sorted_transactions[row]
        print("Transaction passed to HistoryTransactionPreviewForm:", transaction)
        dialog = HistoryTransactionPreviewForm(transaction, self.librarian_id, self)
        dialog.exec()


# To run the app
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv) #create Qt application instance
    window = LibraryTransactionSystem()   #create and show main window 
    nav_manager._current_window = window #set current window in navigation manager
    #dispkay window and start event loop
    window.show() 
    sys.exit(app.exec())
