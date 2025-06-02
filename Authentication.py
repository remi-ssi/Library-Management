"""
PLACEHOLDER PALANG PO YUNG GIF! 
wait lang kasiii 
lalagyan ko red yung border kapag nagkamali si user ng input pero next time na ah hehehe

username: jas
password: qtqt
"""

import sys
import sqlite3
import bcrypt #for password hashing

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QMovie
from PySide6.QtWidgets import (
    QApplication, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout,
    QSpacerItem, QSizePolicy, QHBoxLayout
)

from db_seeder import DatabaseSeeder

def initialize_database():
    import os
    db_exists = os.path.exists("bjrsLib.db")

    if not db_exists:
        print("Database not found. Creating and seeding database...")
        seeder = DatabaseSeeder
        seeder.seed_all()
    else:
        try:
            conn = sqlite3.connect("bjrsLib.db")
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM Librarian")
            librarian_count = cursor.fetchone()[0]

            if librarian_count == 0:
                print("Database exists but is empty. Seeding data...")
                seeder = DatabaseSeeder()
                seeder.seed_all()
            else: 
                print("Database is ready")
            conn.close()

        except sqlite3.Error as e:
            print(f"Database error, attempting to seed: {e}")
            seedder = DatabaseSeeder()
            seeder.seed_all()

#The authentication inherits the QWidget


class Authentication(QWidget): 
    def __init__(self):
        super().__init__() #GIVEN NA TO EVERYTIME

        self.setWindowTitle("Library Management System")
        self.setFixedSize(900,600) #width,height
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f1efe3;
            }
        """)

        label = QLabel("Welcome to BJRS Library")
        font = QFont()
        font.setPointSize(30)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setContentsMargins(450,100,0,0) #left, top, right, bottom

        #For Gif
        self.gif_label = QLabel()
        self.movie = QMovie("assets/book2.gif")
        self.movie.setScaledSize(QSize(250,250)) #width, height
        self.gif_label.setMovie(self.movie)
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setContentsMargins(100,20,0,0) #left, top, right, bottom
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
        
        #ANG PURPOSE NITO IS PARA MAGKAPATONG YUNG USERNAME NA LABEL AT USERNAME NA INPUT!
        username_v_layout = QVBoxLayout()
        username_v_layout.addWidget(username_label)
        username_v_layout.addWidget(self.username_input)
        
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
        
        #PATONG YUNG PASSWORD NA TEXT AT IINPUT-AN
        password_v_layout = QVBoxLayout()
        password_v_layout.addWidget(password_label)
        password_v_layout.addWidget(self.password_input)
        

        # PARA NASA RIGHT SIDE LANG YUNG YUNG USERNAME AT PASSWORD KASI ANG NASA LEFT IS SI GIF SO MAY MALAKING PARANG PADDING SIYA
        h_layout_user = QHBoxLayout()
        h_layout_user.addSpacerItem(QSpacerItem(40,20, QSizePolicy.Expanding, QSizePolicy.Minimum)) #width, height
        h_layout_user.addLayout(username_v_layout)
        h_layout_user.setContentsMargins(0,0,20,0) #left, top, right, bottom

        # Horizontal layout of the password
        h_layout_password = QHBoxLayout()
        h_layout_password.addSpacerItem(QSpacerItem(40,20, QSizePolicy.Expanding, QSizePolicy.Minimum)) #width, height
        h_layout_password.addLayout(password_v_layout)
        h_layout_password.setContentsMargins(0,0,20,0) #left, top, right, bottom

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
        signup_label.setContentsMargins(180,20,0,0)
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
        right_layout.addStretch()
        right_layout.addWidget(signup_label)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        right_layout.addWidget(self.error_label)


        # Main horizontal layout: GIF on the left, form on the right
        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        main_v_layout = QVBoxLayout()
        main_v_layout.addLayout(top_layout)
        main_v_layout.addLayout(main_layout)
        self.setLayout(main_v_layout)

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username:
            self.error_label.setText("Please enter your username!")
            self.error_label.setContentsMargins(180,20,0,0)
            return
        
        if not password:
            self.error_label.setText("Please enter your password!")
            self.error_label.setContentsMargins(180,20,0,0)
            return
        
        try:
            conn = sqlite3.connect("bjrsLib.db")
            cursor = conn.cursor()
            cursor.execute("SELECT LibPass from Librarian WHERE LibUsername =?", (username,))
            result = cursor.fetchone()

            if result:
                stored_hashed_password = result[0]

                if isinstance(stored_hashed_password, str):
                    stored_hashed_password = stored_hashed_password.encode("utf-8")

                if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
                    print("Login successful!")
                    self.dashboard = Dashboard()
                    self.dashboard.show()
                    self.close()
                    # You can emit a signal or open the next screen here
                    return
                else:
                    self.error_label.setText("Invalid username or password.")
            else:
                self.error_label.setText("Invalid username or password.")

        except sqlite3.Error as e:
            print("Database error:", e)
            self.login_error.setText("Database error. Please try again later.")
        finally:
            conn.close() 

    def open_signUp(self):
        # Open the SignUp screen 
        self.signup_window = SignUp()
        self.signup_window.show()

#HI JASSMINEEEEEE DITOO KAAAAAAA!!!!

class SignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Up")
        self.setFixedSize(900,600)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #f1efe3;
            }
        """)

        
        label = QLabel("Create an Account")
        font = QFont()
        font.setPointSize(28)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setContentsMargins(200,100,0,0) #left, top, right, bottom




        #connect to database
        self.conn = sqlite3.connect("bjrsLib.db")
        self.cursor = self.conn.cursor()

        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

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
        form_layout.addSpacing(10)
        form_layout.addWidget(signup_button, alignment=Qt.AlignmentFlag.AlignCenter)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.error_label)
        form_layout.addStretch()

    # PARA GITNA SHA
        outer_layout = QVBoxLayout()
        outer_layout.addStretch()  # top 

        h_center = QHBoxLayout()
        h_center.addStretch()  # left 
        h_center.addLayout(form_layout)
        h_center.addStretch()  # right 

        outer_layout.addLayout(h_center)
        outer_layout.addStretch()  # bottom 

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
    
    def usernameExists(self, username):
        query = "SELECT COUNT (*) FROM Librarian WHERE LibUsername = ?"
        result = self.cursor.execute(query, (username,)).fetchone()
        return result[0]>0


    def handle_signup(self):
        username = self.username_input.text().strip()
        lname = self.lname_input.text().strip ()
        fname = self.fname_input.text().strip()
        mname = self.mname_input.text ().strip ()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
       

        if not username:
            self.error_label.setText("Email cannot be empty.")
            self.username_input.setStyleSheet(self.input_style(error=True))
            return

        if self.usernameExists(username):
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
        hashed_password_str = hashedPass.decode('utf-8')
        insert_query = "INSERT INTO Librarian (LibUsername, LibPass) VALUES (?, ?)"
        self.cursor.execute(insert_query, (username, hashedPass))
        self.conn.commit()
        
        self.error_label.setStyleSheet("color: green; font-weight: bold;")
        self.error_label.setText("Account created successfully!")





if __name__ == "__main__":

    initialize_database()
    
    #This runs the program
    app = QApplication(sys.argv)

    default_font = QFont("Times New Roman")
    app.setFont(default_font)
    app.setStyleSheet("""
        QLabel {color: #4A4947}         
    """)

    window = Authentication()
    window.show()
    app.exec()