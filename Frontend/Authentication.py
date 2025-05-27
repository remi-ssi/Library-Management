"""
PLACEHOLDER PALANG PO YUNG GIF! 
wait lang kasiii 
lalagyan ko red yung border kapag nagkamali si user ng input pero next time na ah hehehe

username: jas
password: qtqt
"""

import sys

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QMovie
from PySide6.QtWidgets import (
    QApplication, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout,
    QSpacerItem, QSizePolicy, QHBoxLayout
)

#The authentication inherits the QWidget
class Authentication(QWidget): 
    def __init__(self):
        super().__init__() #GIVEN NA TO EVERYTIME

        self.setWindowTitle("Library Management System")
        self.setFixedSize(800,600) #width,height


        label = QLabel("Welcome to BJRS Library")
        font = QFont()
        font.setPointSize(28)
        label.setFont(font)
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setContentsMargins(330,100,0,0) #left, top, right, bottom

        #For Gif
        self.gif_label = QLabel()
        self.movie = QMovie("assets/book2.gif")
        self.movie.setScaledSize(QSize(220,220)) #width, height
        self.gif_label.setMovie(self.movie)
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setContentsMargins(90,20,0,0) #left, top, right, bottom
        self.movie.start()

        #Username or Email
        username_label = QLabel("Username")
        font = QFont()
        font.setPointSize (20)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username or email")
        self.username_input.setFixedHeight(40)
        self.username_input.setFixedWidth(300)
        self.username_input.setStyleSheet("""
        QLineEdit {
            border: 2px solid #B7966B;     /* border width and color */
            border-radius: 10px;           /*  rounded corners */
            padding: 8px;                  /*  space inside the textbox */
            font-size: 16px;               /*  font size  */
            background-color: #F0ECE9;
        }

        QLineEdit:focus {
            border: 3px solid #714423;     /*  border color when selected (focused) */
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
        self.password_input.setFixedHeight(40)
        self.password_input.setFixedWidth(300)
        self.password_input.setStyleSheet("""
        QLineEdit {
            border: 2px solid #B7966B;     /* border width and color */
            border-radius: 10px;           /*  rounded corners */
            padding: 8px;                  /*  space inside the textbox */
            font-size: 16px;               /*  font size */
            background-color: #F0ECE9;
        }

        QLineEdit:focus {
            border: 3px solid #714423;     /*  border color when selected (focused) */
        }
    """)
        
        #PATONG YUNG PASSWORD NA TEXT AT IINPUT-AN
        password_v_layout = QVBoxLayout()
        password_v_layout.addWidget(password_label)
        password_v_layout.addWidget(self.password_input)
        

        # PARA NASA RIGHT SIDE LANG YUNG YUNG USERNAME AT PASSWORD KASI ANG NASA LEFT IS SI GIF SO MAY MALAKING PARANG PADDING SIYA
        # Make the username input to the right
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
        signup_label.setTextFormat(Qt.TextFormat.RichText)
        signup_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        signup_label.setOpenExternalLinks(False)  
        signup_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Connect link click 
        signup_label.linkActivated.connect(self.open_signup)       

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
        if username == "jas" and password == "qtqt": #WAIT BABAGUHIN THIS PAG MAY DATABASE NA
            self.error_label.setText("Invalid username or password.")
            self.dashboard = Dashboard()
            self.dashboard.show()
            self.close()
        else:
            self.error_label.setText("Invalid Username or Password.")

    def open_signup(self, link):
        # Open the SignUp screen 
        self.signup_window = SignUp()
        self.signup_window.show()

#HI JASSMINEEEEEE DITOO KAAAAAAA!!!!
class SignUp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sign Up")
        self.setFixedSize(400, 300)
        label = QLabel("ZZZzzzzz Antok na me Jas")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.setFixedSize(800, 600)
        label = QLabel("Welcome to the Dashboard!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)



#This runs the program
app = QApplication(sys.argv)

default_font = QFont("Times New Roman")
app.setFont(default_font)
app.setStyleSheet("""
      QLabel {color: #5C4033}         
 """)

window = Authentication()
window.show()
app.exec()