import sys
import sqlite3
import bcrypt #for password hashing
import books

from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QMovie
from PySide6.QtWidgets import (
    QApplication, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout,
    QSpacerItem, QSizePolicy, QHBoxLayout
)
#initialize database from the seeder
from tryDatabase import DatabaseSeeder
from navbar_logic import nav_manager
    
#The authentication inherits the QWidget
class Authentication(QWidget): 
    _current_librarian_id = None

    @classmethod
    def set_current_librarian_id(cls, librarian_id):
        """Set the current librarian ID after login."""
        cls._current_librarian_id = librarian_id

    @classmethod
    def get_current_librarian_id(cls):
        """Get the current librarian ID."""
        if cls._current_librarian_id is None:
            raise ValueError("No librarian is currently logged in.")
        return cls._current_librarian_id
    
    def __init__(self):
        super().__init__() #GIVEN NA TO EVERYTIME
        self.db_seeder = DatabaseSeeder()

        self.setWindowTitle("Library Management System")
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f1efe3;
            }
        """)

        label = QLabel("Welcome to BJRS Library")
        font = QFont()
        font.setPointSize(45)
        label.setFont(font)
        label.setContentsMargins(0,100,0,20) #left, top, right, bottom 
        label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        label.setStyleSheet("""color:#714423 """)

        #For Gif
        self.gif_label = QLabel()
        self.movie = QMovie("assets/book2.gif")
        self.movie.setScaledSize(QSize(280,280)) #width, height
        self.gif_label.setMovie(self.movie)
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setContentsMargins(0,20,0,0) #left, top, right, bottom
        self.movie.start()

        #Username or Email
        username_label = QLabel("Email")
        font = QFont()
        font.setPointSize (20)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter email")
        self.username_input.setFixedHeight(40)
        self.username_input.setFixedWidth(300)
        self.username_input.setStyleSheet("""
        QLineEdit {
            border: 2px solid #B7966B;     /* border width and color */
            border-radius: 10px;           /*  rounded corners */
            padding: 8px;                  /*  space inside the textbox */
            font-size: 16px;               /*  font size  */
            background-color: #F0ECE9;
            color: #4A4947; /* user input text color */                              
        }

        QLineEdit:focus {
            border: 3px solid #714423;     /*  border color when selected (focused) */
        }
        QLineEdit::placeholder {
            color: #A0A0A0; /* placeholder text color */
        }    
    """)
        
        # Email error label
        self.email_error_label = QLabel("")
        self.email_error_label.setStyleSheet("color: red; font-weight: bold; font: 14px;")
        self.email_error_label.setFixedWidth(300)
        self.email_error_label.hide()  # Initially hidden
        
        # Connect text change to clear error
        self.username_input.textChanged.connect(self.clear_email_error)
        
        #ANG PURPOSE NITO IS PARA MAGKAPATONG YUNG USERNAME NA LABEL AT USERNAME NA INPUT!
        username_v_layout = QVBoxLayout()
        username_v_layout.addWidget(username_label)
        username_v_layout.addWidget(self.username_input)
        username_v_layout.addWidget(self.email_error_label)
        
        #Password
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)   #para nakatago yung password pag ittype
        self.password_input.setFixedHeight(40)
        self.password_input.setFixedWidth(300)
        self.password_input.setStyleSheet("""
        QLineEdit {
            border: 2px solid #B7966B;     /* border width and color */
            border-radius: 10px;           /*  rounded corners */
            padding: 8px;                  /*  space inside the textbox */
            font-size: 16px;               /*  font size */
            background-color: #F0ECE9;
            color: #4A4947; /* user input text color */                              
        }

        QLineEdit:focus {
            border: 3px solid #714423;     /*  border color when selected (focused) */
        }
        QLineEdit::placeholder {
            color: #A0A0A0; /* placeholder text color */
        }                                  
    """)
        
        # Password error label
        self.password_error_label = QLabel("")
        self.password_error_label.setStyleSheet("color: red; font-weight: bold; font: 14px;")
        self.password_error_label.setFixedWidth(300)
        self.password_error_label.hide()  # Initially hidden
        
        # Connect text change to clear error
        self.password_input.textChanged.connect(self.clear_password_error)
        
        #PATONG YUNG PASSWORD NA TEXT AT IINPUT-AN
        password_v_layout = QVBoxLayout()
        password_v_layout.addWidget(password_label)
        password_v_layout.addWidget(self.password_input)
        password_v_layout.addWidget(self.password_error_label)
        
        # PARA NASA RIGHT SIDE LANG YUNG YUNG USERNAME AT PASSWORD KASI ANG NASA LEFT IS SI GIF SO MAY MALAKING PARANG PADDING SIYA
        h_layout_user = QHBoxLayout()
        h_layout_user.addSpacerItem(QSpacerItem(80,20, QSizePolicy.Expanding, QSizePolicy.Minimum)) #width, height
        h_layout_user.addLayout(username_v_layout)
        h_layout_user.setContentsMargins(0,0,20,0) #left, top, right, bottom

        # Horizontal layout of the password
        h_layout_password = QHBoxLayout()
        h_layout_password.addSpacerItem(QSpacerItem(40,20, QSizePolicy.Expanding, QSizePolicy.Minimum)) #width, height
        h_layout_password.addLayout(password_v_layout)
        h_layout_password.setContentsMargins(0,0,20,15) #left, top, right, bottom

        #Login Button
        login_button = QPushButton("Log In")
        login_button.setFixedHeight(40)
        login_button.setFixedWidth(150)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #B7966B;
                color: white;
                border-radius: 10px;
                font-size: 16px;
            }
                                   
            QPushButton:hover {
                background-color: #A67B5B;
            }
        """)
        login_button.clicked.connect(self.handle_login) 

        #FOR SIGNUP!!!!
        signup_label = QLabel()
        signup_label.setText('Don\'t have an account? <a href="signup">Sign Up</a>')
        signup_label.setContentsMargins(0,20,0,50)
        signup_label.setTextFormat(Qt.TextFormat.RichText)
        signup_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        signup_label.setOpenExternalLinks(False)  
        signup_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Connect link click 
        signup_label.linkActivated.connect(self.open_signUp)       

        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(50, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))  # 50 px space before button
        button_layout.addWidget(login_button) 

        #CONSIST OF THE TEXT LANG HEHEHE YUNG WELCOME BJRS
        #Top Layout
        top_layout = QVBoxLayout()
        top_layout.addWidget(label)

        #ONLY FOR GIF!
        #Left Layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.gif_label)
        left_layout.addStretch()

        #USERNAME, PASSWORD, LOG IN BUTTON
        # Right side layout for label and input fields
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 50, 50) #left, top, right, bottom
        right_layout.addSpacing(40)
        right_layout.addLayout(h_layout_user)
        right_layout.addSpacing(25)
        right_layout.addLayout(h_layout_password)
        right_layout.addSpacing(40)
        right_layout.addLayout(button_layout)
        
        # General error label (for login failures)
        self.general_error_label = QLabel("")
        self.general_error_label.setStyleSheet("color: red; font-weight: bold; font: 15px;")
        self.general_error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.general_error_label.setContentsMargins(50,10,0,0)
        self.general_error_label.hide()  # Initially hidden
        right_layout.addWidget(self.general_error_label)

        # Create a layout to center the form (right_layout) horizontally
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addLayout(left_layout)
        center_layout.addLayout(right_layout)
        center_layout.addStretch()

        # Combine GIF + Form in a vertical layout to center vertically too
        middle_layout = QVBoxLayout()
        middle_layout.setContentsMargins(0, 50, 0, 0)
        middle_layout.addStretch()
        middle_inner_layout = QHBoxLayout()
        middle_inner_layout.addLayout(left_layout)
        middle_inner_layout.addLayout(center_layout)
        middle_layout.addLayout(middle_inner_layout)
        middle_layout.addStretch()

        # This keeps it at the very bottom, centered
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(signup_label)
        bottom_layout.addStretch()

        main_v_layout = QVBoxLayout()
        main_v_layout.addLayout(top_layout)
        main_v_layout.addLayout(middle_layout)
        main_v_layout.addLayout(bottom_layout)

        self.setLayout(main_v_layout)
        self.showMaximized() 
     
    def clear_email_error(self):
        """Clear email error when user starts typing"""
        self.email_error_label.hide()
        self.email_error_label.setText("")
        
    def clear_password_error(self):
        """Clear password error when user starts typing"""
        self.password_error_label.hide()
        self.password_error_label.setText("")
        
    def clear_general_error(self):
        """Clear general error"""
        self.general_error_label.hide()
        self.general_error_label.setText("")
     
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        # Clear all previous errors
        self.clear_email_error()
        self.clear_password_error()
        self.clear_general_error()
        
        # Validate fields
        has_error = False
        
        if not username:
            self.email_error_label.setText("Email field is required")
            self.email_error_label.show()
            has_error = True
        
        if not password:
            self.password_error_label.setText("Password field is required")
            self.password_error_label.show()
            has_error = True
            
        # If there are field errors, don't proceed with login
        if has_error:
            return
        
        # Proceed with login validation
        if self.db_seeder.verify_librarian_login(username, password):

            librarians = self.db_seeder.get_all_records("Librarian")
            librarian = next((lib for lib in librarians if lib ['LibUsername'] == username), None)
            if librarian:
                librarian_id = librarian["LibrarianID"]
                self.set_current_librarian_id(librarian_id)
                nav_manager.set_librarian_id(librarian_id)
                print("Log in successful: ", librarian_id)
                self.books_window = books.CollapsibleSidebar()  # use correct variable and class
                nav_manager._current_window = self.books_window
                self.books_window.show()
                self.close()
            else:
                self.general_error_label.setText("Librarian Not Found...")
                self.general_error_label.show()
        else:
            self.general_error_label.setText("Invalid email or password")
            self.general_error_label.show()

    def open_signUp(self):
        # Open the SignUp screen 
        self.signup_window = SignUp()
        self.signup_window.show()

#FOR JASMINE

class SignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.db_seeder = DatabaseSeeder()
        self.setWindowTitle("Sign Up")
        self.showMaximized() 

        
        self.setStyleSheet("""
            QWidget {
                background-color: #f1efe3;
            }
        """)

        label = QLabel("Create an Account")
        font = QFont()
        font.setPointSize(40)
        label.setFont(font)
        label.setContentsMargins(360,40,0,20) #left, top, right, bottom
        label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        label.setStyleSheet("""color:#714423 """)


        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # For the GIF
        self.gif_label = QLabel()
        self.movie = QMovie("assets/book2.gif")
        self.movie.setScaledSize(QSize(280, 280))  # adjust size as needed
        self.gif_label.setMovie(self.movie)
        self.gif_label.setContentsMargins(0,0,0,100)
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie.start()


        # EMAIL (CAPITALLL GALIT SI SHELLEY) 
        username_label = QLabel("Email")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Email")
        self.username_input.setFixedHeight(40)
        self.username_input.setFixedWidth(300)
        self.username_input.setStyleSheet(self.input_style())

        # LAST NAME 
        lname_label = QLabel("Last Name")
        self.lname__input = QLineEdit()
        self.lname__input.setPlaceholderText("Last Name")
        self.lname__input.setFixedHeight(40)
        self.lname__input.setFixedWidth(300)
        self.lname__input.setStyleSheet(self.input_style())

         # FIRST NAME 
        fname_label = QLabel("First Name")
        self.fname_input = QLineEdit()
        self.fname_input.setPlaceholderText("First Name")
        self.fname_input.setFixedHeight(40)
        self.fname_input.setFixedWidth(300)
        self.fname_input.setStyleSheet(self.input_style())

        # MIDDLE NAME
        mname_label = QLabel("Middle Name")
        self.mname_input = QLineEdit()
        self.mname_input.setPlaceholderText("Middle Name")
        self.mname_input.setFixedHeight(40)
        self.mname_input.setFixedWidth(300)
        self.mname_input.setStyleSheet(self.input_style())

        # PASSWORD
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(40)
        self.password_input.setFixedWidth(300)
        self.password_input.setStyleSheet(self.input_style())

        # PASSWORD NGANI
        confirm_label = QLabel("Confirm Password")
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.setFixedHeight(40)
        self.confirm_input.setFixedWidth(300)
        self.confirm_input.setStyleSheet(self.input_style())
        
        # SIGN UP BUTTON CLICK
        signup_button = QPushButton("Sign Up")
        signup_button.setFixedHeight(40)
        signup_button.setFixedWidth(150)
        signup_button.setStyleSheet("""
            QPushButton {
                background-color: #B7966B;
                color: white;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #A67B5B;
            }
        """)
        signup_button.clicked.connect(self.handle_signup)

        # "Already have an account? Log In" link
        login_link = QLabel()
        login_link.setText('Already have an account? <a href="login">Log In</a>')
        login_link.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_link.setContentsMargins(0,10,0,20)
        login_link.setTextFormat(Qt.TextFormat.RichText)
        login_link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        login_link.setOpenExternalLinks(False)

        # Connect link click 
        login_link.linkActivated.connect(self.open_login)

        top_layout = QHBoxLayout()
        top_layout.addWidget(label)

        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(50, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))  # 50 px space before button
        button_layout.addWidget(signup_button) 

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(login_link)
        bottom_layout.setContentsMargins(0,0,0,20)

        # BASTA LAYOUT NG INPUT
        username_layout = QVBoxLayout()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)

        # Last Name
        lname_layout = QVBoxLayout()
        lname_layout.addWidget(lname_label)
        lname_layout.addWidget(self.lname__input)

        # First Name
        fname_layout = QVBoxLayout()
        fname_layout.addWidget(fname_label)
        fname_layout.addWidget(self.fname_input)

        # Middle Name
        mname_layout = QVBoxLayout()
        mname_layout.addWidget(mname_label)
        mname_layout.addWidget(self.mname_input)

        password_layout = QVBoxLayout()
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)

        confirm_layout = QVBoxLayout()
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)

        form_layout = QVBoxLayout()
        form_layout.addLayout(username_layout)
        form_layout.addSpacing(10)
        form_layout.addLayout(lname_layout)
        form_layout.addSpacing(10)
        form_layout.addLayout(fname_layout)
        form_layout.addSpacing(10)
        form_layout.addLayout(mname_layout)
        form_layout.addSpacing(10)
        form_layout.addLayout(password_layout)
        form_layout.addSpacing(10)
        form_layout.addLayout(confirm_layout)
        form_layout.addSpacing(30)
        form_layout.addWidget(signup_button, alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addSpacing(10)
        form_layout.addWidget(self.error_label)
     

        # Layout for form on the right
        form_right_layout = QVBoxLayout()
        form_right_layout.addSpacing(20)
        form_right_layout.addLayout(form_layout)
        form_right_layout.addStretch()

        # Layout that puts GIF on the left and form on the right
        main_h_layout = QHBoxLayout()
        main_h_layout.addStretch()
        main_h_layout.addWidget(self.gif_label)
        main_h_layout.addSpacing(80)  # space between GIF and form
        main_h_layout.addLayout(form_right_layout)
        main_h_layout.addStretch()

        # Vertically center everything
        outer_layout = QVBoxLayout()
        outer_layout.addLayout(top_layout)
        outer_layout.addStretch()
        outer_layout.addLayout(main_h_layout)
        outer_layout.addStretch()
        outer_layout.addLayout(bottom_layout)

        self.setLayout(outer_layout)


    def input_style(self, error=False): 
        border_color = "#FF0000" if error else "#B7966B"
        return f"""
            QLineEdit {{
                border: 2px solid {border_color};
                border-radius: 10px;
                padding: 8px;
                font-size: 16px;
                background-color: #F0ECE9;
                color: #4A4947; /* user input text color */                              
        }}

        QLineEdit:focus {{
            border: 3px solid #714423;     /*  border color when selected (focused) */
        }}
        QLineEdit::placeholder {{
            color: #A0A0A0; /* placeholder text color */
        }}
        """

    def open_login(self):
        # Close the SignUp window and go back to login
        self.close()

    def handle_signup(self):
        username = self.username_input.text().strip()
        lname = self.lname__input.text().strip ()
        fname = self.fname_input.text().strip()
        mname = self.mname_input.text ().strip ()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        if not username:
            self.error_label.setText("Email cannot be empty.")
            self.username_input.setStyleSheet(self.input_style(error=True))
            return

        if self.db_seeder.findUsername(username=username):
            self.error_label.setText("Email already exists. Please enter a new username.")
            self.username_input.setStyleSheet(self.input_style(error=True))
            return
        
        if not password:
            self.error_label.setText("Password cannot be empty.")
            self.password_input.setStyleSheet(self.input_style(error=True))
            return

        if password != confirm:
            self.error_label.setText("Passwords do not match.")
            self.password_input.setStyleSheet(self.input_style(error=True))
            self.confirm_input.setStyleSheet(self.input_style(error=True))
            return
        
        #PARA YUNG HASHESD PASS YUNG MAISTORE SA DATABASE
        hashedPass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
       # hashed_password_str = hashedPass.decode('utf-8')
       
       # self.db_seeder.preSeed_all_tables()
        self.db_seeder.seed_data(
            tableName="Librarian",
            data=[
                {
                    "LibUsername": username,
                    "LibPass": hashedPass,
                    "FName": fname,
                    "LName": lname,
                    "MName": mname
                }
            ],
            columnOrder=["LibUsername", "LibPass", "FName", "LName", "MName"]
            )
        
        # Show success message briefly then go back to login
        self.error_label.setStyleSheet("color: green; font-weight: bold;")
        self.error_label.setText("Account created successfully! Redirecting to login...")
        
        # Use QTimer to delay the redirect
        QTimer.singleShot(2000, self.close)  # Close after 2 seconds

if __name__ == "__main__":
    #This runs the program
    app = QApplication(sys.argv)

    default_font = QFont("Times New Roman")
    app.setFont(default_font)
    app.setStyleSheet("""
        QLabel {color: #4A4947}         
    """)

    window = Authentication()
    nav_manager.initialize(app)
    #window.showFullScreen()
    window.show() 
    app.exec()