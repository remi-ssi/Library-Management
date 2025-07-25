import sys
import sqlite3
import bcrypt 
import Dashboard
import re
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv 
from PySide6.QtCore import Qt, QSize, QTimer 
from PySide6.QtGui import QFont, QMovie, QIcon
from PySide6.QtWidgets import (
    QApplication, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout,
    QSpacerItem, QSizePolicy, QHBoxLayout, QFrame, QMessageBox
)
#initialize database from the seeder
from tryDatabase import DatabaseSeeder 
from navbar_logic import nav_manager 
from ResetPasswordDialog import ResetPasswordDialog 

 
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
        super().__init__() 
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
        label.setContentsMargins(0,100,0,20)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        label.setStyleSheet("""color:#714423 """)

        #For Gif
        self.gif_label = QLabel()
        self.movie = QMovie("assets/book2.gif")
        self.movie.setScaledSize(QSize(280,280)) 
        self.gif_label.setMovie(self.movie)
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gif_label.setContentsMargins(0,20,0,0)
        self.movie.start()

        #Email
        email_label = QLabel("Email")
        font = QFont()
        font.setPointSize (20)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")
        self.email_input.setFixedHeight(40)
        self.email_input.setFixedWidth(300)
        self.email_input.setStyleSheet("""
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
        self.email_error_label.hide()  
        
        # Connect text change to clear error
        self.email_input.textChanged.connect(self.clear_email_error)
        
        #Layout for Email and EmailLabel
        email_v_layout = QVBoxLayout()
        email_v_layout.addWidget(email_label)
        email_v_layout.addWidget(self.email_input)
        email_v_layout.addWidget(self.email_error_label)
        
        #Password
        password_label = QLabel("Password")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)   
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
        
        # Eye button for password
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setIcon(QIcon("assets/eye-closed.png")) 
        self.toggle_password_btn.setFixedSize(30, 30)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(183, 150, 107, 0.1);
                border-radius: 15px;
            }
        """)
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)

        # Container for password input and toggle button
        password_container = QWidget()
        password_container.setFixedHeight(40)
        password_container.setFixedWidth(300)
        
        # Horizontal layout for password input and toggle button
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(0)
        password_layout.addWidget(self.password_input)
        password_layout.addWidget(self.toggle_password_btn)
        password_layout.addSpacing(5)  
        
        # Password error label
        self.password_error_label = QLabel("")
        self.password_error_label.setStyleSheet("color: red; font-weight: bold; font: 14px;")
        self.password_error_label.setFixedWidth(300)
        self.password_error_label.hide()  
        
        # Connect text change to clear error
        self.password_input.textChanged.connect(self.clear_password_error)
        
        # Password layout with label and input field
        password_v_layout = QVBoxLayout()
        password_v_layout.addWidget(password_label)
        password_v_layout.addWidget(password_container)  
        password_v_layout.addWidget(self.password_error_label)

        password_v_layout.addSpacing(25)

        # Forgot Password Button
        forgot_password_btn = QPushButton("Forgot Password?")
        forgot_password_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #714423;
                border: none;
                font-size: 14px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #A67B5B;
            }
        """)
        forgot_password_btn.setCursor(Qt.PointingHandCursor)
        forgot_password_btn.clicked.connect(self.open_forgot_password)

        password_v_layout.addWidget(forgot_password_btn)
        
        # Right Side
        h_layout_user = QHBoxLayout()
        h_layout_user.addSpacerItem(QSpacerItem(80,20, QSizePolicy.Expanding, QSizePolicy.Minimum)) 
        h_layout_user.addLayout(email_v_layout)
        h_layout_user.setContentsMargins(0,0,20,0) 

        # Horizontal layout of the password
        h_layout_password = QHBoxLayout()
        h_layout_password.addSpacerItem(QSpacerItem(40,20, QSizePolicy.Expanding, QSizePolicy.Minimum)) 
        h_layout_password.addLayout(password_v_layout)
        h_layout_password.setContentsMargins(0,0,20,15) 

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


        #For Signup
        signup_label = QLabel()
        signup_label.setText('Don\'t have an account? <a href="signup">Sign Up</a>') 
        signup_label.setContentsMargins(0,20,0,50)
        signup_label.setTextFormat(Qt.TextFormat.RichText)
        signup_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        signup_label.setOpenExternalLinks(False)  
        signup_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Connect link click 
        signup_label.linkActivated.connect(self.open_signUp)       

        # For Login Button
        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(50, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)) 
        button_layout.addWidget(login_button) 

        #"WELCOME TO BJRS Library"
        #Top Layout
        top_layout = QVBoxLayout()
        top_layout.addWidget(label)

        #GIF
        #Left Layout
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.gif_label)
        left_layout.addStretch()

        #Username, Password and Login button
        # Right side layout for label and input fields
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0, 0, 50, 50) 
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
        self.general_error_label.hide()  
        right_layout.addWidget(self.general_error_label)

        # Create a layout to center the form (right_layout) horizontally
        center_layout = QHBoxLayout()
        center_layout.addStretch()
        center_layout.addLayout(left_layout)
        center_layout.addLayout(right_layout)
        center_layout.addStretch()

        # Combine GIF + Form in a vertical layout to center vertically 
        middle_layout = QVBoxLayout()
        middle_layout.setContentsMargins(0, 50, 0, 0)
        middle_layout.addStretch()
        middle_inner_layout = QHBoxLayout()
        middle_inner_layout.addLayout(center_layout)
        middle_layout.addLayout(middle_inner_layout)
        middle_layout.addStretch()

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

    
    def toggle_password_visibility(self):
        # toggle the visibility of the password input
        if self.password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)  
            self.toggle_password_btn.setIcon(QIcon("assets/eye-open.png"))
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)  
            self.toggle_password_btn.setIcon(QIcon("assets/eye-closed.png"))

     
    def handle_login(self):
        email = self.email_input.text()
        password = self.password_input.text()

        self.clear_email_error()
        self.clear_password_error()
        self.clear_general_error()

        has_error = False

        if not email:
            self.email_error_label.setText("Email field is required")
            self.email_error_label.show()
            has_error = True

        if not password:
            self.password_error_label.setText("Password field is required")
            self.password_error_label.show()
            has_error = True

        if has_error:
            return

        if self.db_seeder.verify_librarian_login(email, password):
            librarians = self.db_seeder.get_all_records(tableName="Librarian", id="")
            librarian = next((lib for lib in librarians if lib['LibUsername'] == email), None)
            if librarian:
                librarian_id = librarian["LibrarianID"] 
                self.set_current_librarian_id(librarian_id)
                nav_manager.set_librarian_id(librarian_id)
                print("Log in successful: ", librarian_id)
                self.dashboard_window = Dashboard.LibraryDashboard() 
                self.dashboard_window.librarian_id = librarian_id 
                nav_manager._current_window = self.dashboard_window
                self.dashboard_window.show()
                self.close() 
            else:
                self.general_error_label.setText("Librarian Not Found...")
                self.general_error_label.show()
        else:
            self.general_error_label.setText("Invalid email or password")
            self.general_error_label.show()

    def open_forgot_password(self):
        email = self.email_input.text().strip()

        if not email:
            self.email_error_label.setText("Please enter your email to reset password.")
            self.email_error_label.show()
            return

        # Optionally validate if email exists in DB
        if not self.db_seeder.findUsername(email):
            self.general_error_label.setText("Email not found.")
            self.general_error_label.show()
            return

        self.confirm_email_dialog = ConfirmEmailDialog(email, self, purpose="reset")
        self.confirm_email_dialog.setWindowTitle("Reset Password - Confirm Email")
        self.confirm_email_dialog.show()

    def open_signUp(self):
        # Open the SignUp screen 
        self.signup_window = SignUp()
        self.signup_window.show()

      # "Forgot Password?" link
        forgot_password_label = QLabel('<a href="#">Forgot password?</a>')
        forgot_password_label.setTextFormat(Qt.TextFormat.RichText)
        forgot_password_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        forgot_password_label.setOpenExternalLinks(False)
        forgot_password_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        forgot_password_label.linkActivated.connect(self.open_forgot_password)

    def proceed_with_password_reset(self, email, otp=None):
        self.reset_password_dialog = ResetPasswordDialog(email, otp, self.db_seeder) #Open dialog
        self.reset_password_dialog.show()

class ConfirmEmailDialog(QWidget):
    def __init__(self, email, parent=None, purpose="register"):
        super().__init__(parent)
        self.email = email
        self.parent = parent
        self.purpose = purpose
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Confirm Your Email")
        self.setFixedSize(500, 400)
        # Set proper window flags for a dialog
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
    
        # Make sure window has a background
        self.setAttribute(Qt.WA_TranslucentBackground, False)
        
        # Center dialog on screen
        self.center_on_screen()
        
        self.setStyleSheet("""
            background-color: #f1efe3;
            border-radius: 16px;
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 80, 30, 30)
        
        # Title
        title_label = QLabel("Confirm your email")
        title_label.setFont(QFont("Times New Roman", 18, QFont.Bold))
        title_label.setStyleSheet("color: #714423;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        desc_label = QLabel("We will send an OTP to your email address. Please confirm it to proceed.")
        desc_label.setFont(QFont("Times New Roman", 12))
        desc_label.setStyleSheet("color: #4A4947;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_label.setWordWrap(True)
        
        # Email field 
        email_container = QHBoxLayout()
        email_container.addStretch()
        
        self.email_input = QLineEdit()
        self.email_input.setText(self.email)  
        self.email_input.setReadOnly(True)  
        self.email_input.setFixedHeight(40)
        self.email_input.setFixedWidth(300)
        self.email_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.email_input.setStyleSheet("""
            QLineEdit {
                border-radius: 10px;
                padding: 8px;
                font-size: 15px;
                font-weight: bold;
                color: #5C4033;

            }

        """)
        
        email_container.addWidget(self.email_input)
        email_container.addStretch()
        
        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setFixedWidth(300)
        self.error_label.hide()
        
        # Center buttons
        button_container = QHBoxLayout()
        button_container.addStretch()
        
        # Confirm button
        self.confirm_btn = QPushButton("Confirm Email")
        self.confirm_btn.setFixedHeight(40)
        self.confirm_btn.setFixedWidth(120)
        self.confirm_btn.setStyleSheet("""
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
        self.confirm_btn.clicked.connect(self.send_otp)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setFixedWidth(120)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #DDDDDD;
                color: #333333;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #CCCCCC;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addSpacing(20)  
        button_layout.addWidget(self.confirm_btn)
        
        button_container.addLayout(button_layout)
        button_container.addStretch()
        
        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(desc_label)
        main_layout.addSpacing(40)
        main_layout.addLayout(email_container)
        main_layout.addWidget(self.error_label)
        main_layout.addStretch()
        main_layout.addLayout(button_container)
        
        self.setLayout(main_layout)
    
    def center_on_screen(self):
        # Center the dialog on the screen
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def send_otp(self):
        email = self.email_input.text().strip()
        
        
        # Generate OTP
        import random
        otp = str(random.randint(100000, 999999)) #6-digit OTP without zeros
        
        # Send email with OTP
        if self.send_real_email(email, otp):
            # Email sent successfully
            self.close()
            self.otp_dialog = OTPVerificationDialog(email, self, otp)
            self.otp_dialog.show()
            
            # Center the OTP dialog on screen
            screen_geometry = QApplication.primaryScreen().geometry()
            x = (screen_geometry.width() - self.otp_dialog.width()) // 2
            y = (screen_geometry.height() - self.otp_dialog.height()) // 2
            self.otp_dialog.move(x, y)
        else:
            # Failed to send email
            self.error_label.setText("Failed to send verification email. Please try again.")
            self.error_label.show()
    
    def send_real_email(self, recipient_email, otp):
        try:

            load_dotenv("email.env") #access the email env file
            
            # Get email credentials from environment variables
            sender_email = os.getenv("EMAIL_ADDRESS") #gets the value of the variable from env
            sender_password = os.getenv("EMAIL_PASSWORD") #gets the value of the variable from env
            
            if not sender_email or not sender_password: 
                print("Email credentials not found in environment variables")
                return False
                
            # Create message
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = recipient_email
            message["Subject"] = "BJRS Library - Email Verification Code"
            
            # Email body
            body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.5;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
                    <h2 style="color: #714423; text-align: center;">BJRS Library Email Verification</h2>
                    <p>Thank you for registering with BJRS Library Management System.</p>
                    <p>Your verification code is:</p>
                    <div style="text-align: center; margin: 20px 0;">
                        <div style="display: inline-block; padding: 10px 20px; background-color: #f1efe3; border: 2px solid #B7966B; border-radius: 5px; font-size: 24px; font-weight: bold; letter-spacing: 5px; color: #714423;">
                            {otp}
                        </div>
                    </div>
                    <p>This code will expire in 10 minutes.</p>
                    <p>If you didn't request this code, please ignore this email.</p>
                    <p style="margin-top: 30px; font-size: 12px; color: #777; text-align: center;">
                        This is an automated message, please do not reply.
                    </p>
                </div>
            </body>
            </html>
            """
            
            # Attach HTML content
            message.attach(MIMEText(body, "html"))
            
            # Connect to SMTP server (using Gmail as example)
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(message)
                
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
        

class OTPVerificationDialog(QWidget):
    def __init__(self, email, parent=None, otp=None):
        super().__init__(parent)
        self.email = email
        self.parent = parent
        # Store the OTP parameter that was passed in
        self.otp = otp if otp else self.generate_otp()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("OTP Verification")
        self.setFixedSize(500, 400)
        # Set proper window flags for a dialog
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)

        # Make sure window has a background
        self.setAttribute(Qt.WA_TranslucentBackground, False)

        self.setStyleSheet("""
            QWidget {
                background-color: #f1efe3;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title_label = QLabel("Verify Your Email")
        title_label.setFont(QFont("Times New Roman", 18, QFont.Bold))
        title_label.setStyleSheet("color: #714423;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Description
        desc_label = QLabel(f"We've sent a verification code to {self.email}. Please enter the code below:")
        desc_label.setFont(QFont("Times New Roman", 12))
        desc_label.setStyleSheet("color: #4A4947;")
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
     
        
        # OTP field
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Enter OTP")
        self.otp_input.setFixedHeight(40)
        self.otp_input.setFixedWidth(350)
        self.otp_input.setMaxLength(6)
        self.otp_input.setContentsMargins(85, 0, 0, 0)  
        self.otp_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.otp_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #B7966B;
                border-radius: 10px;
                padding: 8px;
                font-size: 16px;
                background-color: #F0ECE9;
                color: #4A4947;
                text-align: center; 
            }
            QLineEdit:focus {
                border: 3px solid #714423;
            }
            QLineEdit::placeholder {
                color: #A0A0A0;
            }
        """)
        
     
        # Error label
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        
        # Resend OTP link
        resend_label = QLabel("<a href='resend'>Didn't receive the code? Resend</a>")
        resend_label.setTextFormat(Qt.TextFormat.RichText)
        resend_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        resend_label.setOpenExternalLinks(False)
        resend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        resend_label.linkActivated.connect(self.resend_otp)
        
        # Verify button
        self.verify_btn = QPushButton("Verify Email")
        self.verify_btn.setFixedHeight(40)
        self.verify_btn.setStyleSheet("""
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
        self.verify_btn.clicked.connect(self.verify_otp)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedHeight(40)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #DDDDDD;
                color: #333333;
                border-radius: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #CCCCCC;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.verify_btn)
        
        # Add widgets to main layout
        main_layout.addSpacing(20)
        main_layout.addWidget(title_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(desc_label)
        main_layout.addSpacing(50)
        main_layout.addWidget(self.otp_input)
        main_layout.addWidget(self.error_label)
        main_layout.addSpacing(10)
        main_layout.addWidget(resend_label)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def generate_otp(self):
        # Generate a 6-digit random OTP
        import random
        return str(random.randint(100000, 999999))
    
    def resend_otp(self):
        # Regenerate OTP
        self.otp = self.generate_otp()
        
        # Create ConfirmEmailDialog instance to use its send_real_email method
        confirm_dialog = ConfirmEmailDialog(self.email, self.parent)
        
        # Send email with the new OTP
        if confirm_dialog.send_real_email(self.email, self.otp):
      
            QMessageBox.information(self, "OTP Resent", f"A new OTP has been sent to {self.email}")
        else:

            QMessageBox.warning(self, "Error", f"Failed to resend OTP to {self.email}")
    
    def verify_otp(self):
        print("verify_otp called")
        print("self.parent:", self.parent)
        if hasattr(self.parent, "purpose"):
            print("self.parent.purpose:", self.parent.purpose)
        else:
            print("self.parent has no 'purpose' attribute")
        if hasattr(self.parent, "proceed_with_signup"):
            print("self.parent has proceed_with_signup")
        else:
            print("self.parent does NOT have proceed_with_signup")
        entered_otp = self.otp_input.text().strip()
        if not entered_otp:
            self.error_label.setText("Please enter the OTP.")
            self.error_label.show()
            return

        if entered_otp == self.otp:
            if hasattr(self.parent, "purpose") and self.parent.purpose == "register":
                print("Register flow detected")
                from PySide6.QtWidgets import QMessageBox
                if hasattr(self.parent.parent, "proceed_with_signup"):
                    print("Calling proceed_with_signup")
                    self.parent.parent.proceed_with_signup()
                    print("User created:", self.parent.parent.pending_email)
                    print("All users:", self.parent.parent.db_seeder.get_all_records(tableName="Librarian", id=""))
                    QMessageBox.information(self, "Account Created", "Account created successfully! Redirecting to login...")
                    self.close()
                else:
                    print("No proceed_with_signup!")
            # Password Reset Flow
            elif hasattr(self.parent, "purpose") and self.parent.purpose == "reset":
                if hasattr(self.parent.parent, "proceed_with_password_reset"):
                    self.close()
                    self.parent.parent.proceed_with_password_reset(self.email, self.otp)
        else:
            self.error_label.setText("Incorrect OTP. Please try again.")
            self.error_label.show()


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
        label.setContentsMargins(360,40,0,20) 
        label.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        label.setStyleSheet("""color:#714423 """)


        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red; font-weight: bold;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # For GIF
        self.gif_label = QLabel()
        self.movie = QMovie("assets/book2.gif")
        self.movie.setScaledSize(QSize(280, 280)) 
        self.gif_label.setMovie(self.movie)
        self.gif_label.setContentsMargins(0,0,0,100)
        self.gif_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.movie.start()


        # Email
        email_label = QLabel("Email")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter Email")
        self.email_input.setFixedHeight(40)
        self.email_input.setFixedWidth(300)
        self.email_input.setStyleSheet(self.input_style())

        # Last Name
        lname_label = QLabel("Last Name")
        self.lname__input = QLineEdit()
        self.lname__input.setPlaceholderText("Last Name")
        self.lname__input.setFixedHeight(40)
        self.lname__input.setFixedWidth(300)
        self.lname__input.setStyleSheet(self.input_style())

         # First Name
        fname_label = QLabel("First Name")
        self.fname_input = QLineEdit()
        self.fname_input.setPlaceholderText("First Name")
        self.fname_input.setFixedHeight(40)
        self.fname_input.setFixedWidth(300)
        self.fname_input.setStyleSheet(self.input_style())

        # Middle Name
        mname_label = QLabel("Middle Name")
        self.mname_input = QLineEdit()
        self.mname_input.setPlaceholderText("Middle Name")
        self.mname_input.setFixedHeight(40)
        self.mname_input.setFixedWidth(300)
        self.mname_input.setStyleSheet(self.input_style())

        # Password
        self.toggle_password_btn = QPushButton()
        self.toggle_password_btn.setIcon(QIcon("assets/eye-closed.png"))
        self.toggle_password_btn.setFixedSize(30, 30)
        self.toggle_password_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(183, 150, 107, 0.1);
                border-radius: 15px;
            }
        """)

        password_container, self.password_input = self.create_password_field("Enter password", self.toggle_password_btn)
        self.toggle_password_btn.clicked.connect(
            lambda: self.toggle_password_visibility(self.password_input, self.toggle_password_btn)
        )

        # Confirm Password
        self.toggle_confirm_btn = QPushButton()
        self.toggle_confirm_btn.setIcon(QIcon("assets/eye-closed.png"))
        self.toggle_confirm_btn.setFixedSize(30, 30)
        self.toggle_confirm_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(183, 150, 107, 0.1);
                border-radius: 15px;
            }
        """)

        confirm_container, self.confirm_input = self.create_password_field("Confirm password", self.toggle_confirm_btn)
        self.toggle_confirm_btn.clicked.connect(
            lambda: self.toggle_password_visibility(self.confirm_input, self.toggle_confirm_btn)
        )

        # Signup button
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
        button_layout.addSpacerItem(QSpacerItem(50, 0, QSizePolicy.Fixed, QSizePolicy.Minimum)) 
        button_layout.addWidget(signup_button) 

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(login_link)
        bottom_layout.setContentsMargins(0,0,0,20)

    
        email_layout = QVBoxLayout()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)

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
        password_layout.addWidget(QLabel("Password"))
        password_layout.addWidget(password_container)

        confirm_layout = QVBoxLayout()
        confirm_layout.addWidget(QLabel("Confirm Password"))
        confirm_layout.addWidget(confirm_container)

        form_layout = QVBoxLayout()
        form_layout.addLayout(email_layout)
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
        main_h_layout.addSpacing(80)  
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
        email = self.email_input.text().strip()
        lname = self.lname__input.text().strip()
        fname = self.fname_input.text().strip()
        mname = self.mname_input.text().strip()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        # Field validation 
        if not email or not lname or not fname or not password or not confirm:
            self.error_label.setText("All fields are required.")
            return
        
        # Email validation 
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            self.error_label.setText("Please enter a valid email address.")
            self.email_input.setStyleSheet(self.input_style(error=True))
            return
        else:
        # Reset style if valid
            self.email_input.setStyleSheet(self.input_style(error=False))


        # Password constraints 
        if len(password) < 8:
            self.error_label.setText("Password must be at least 8 characters.")
            return
        if not re.search(r"[A-Z]", password):
            self.error_label.setText("Password must have at least one uppercase letter.")
            return
        if not re.search(r"[a-z]", password):
            self.error_label.setText("Password must have at least one lowercase letter.")
            return
        if not re.search(r"\d", password):
            self.error_label.setText("Password must have at least one digit.")
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            self.error_label.setText("Password must have at least one special character.")
            return
        if password != confirm:
            self.error_label.setText("Passwords do not match.")
            return

        # Username/email uniqueness check 
        if self.db_seeder.findUsername(email):
            self.error_label.setText("     Email already exists.")
            return

        # If all checks pass, open the confirm email dialog 
        self.confirm_email_dialog = ConfirmEmailDialog(email, self, purpose="register")
        self.confirm_email_dialog.show()

        # Store the user data for later use after verification
        self.pending_email = email
        self.pending_lname = lname
        self.pending_fname = fname
        self.pending_mname = mname
        self.pending_password = password

    def proceed_with_signup(self):
        email = self.pending_email
        lname = self.pending_lname
        fname = self.pending_fname
        mname = self.pending_mname
        password = self.pending_password

        # Hash the password
        hashedPass = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        
        self.db_seeder.create_table("Librarian")

        # Create the account in the database
        self.db_seeder.seed_data(
            tableName="Librarian",
            data=[
                {
                    "LibUsername": email,
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

        print("User created:", email)
        print("All users:", self.db_seeder.get_all_records(tableName="Librarian", id=""))

        def go_to_login():
            self.close()
            

        QTimer.singleShot(2000, go_to_login)

    def toggle_password_visibility(self, input_field, toggle_button):
        if input_field.echoMode() == QLineEdit.EchoMode.Password:
            input_field.setEchoMode(QLineEdit.EchoMode.Normal)
            toggle_button.setIcon(QIcon("assets/eye-open.png"))
        else:
            input_field.setEchoMode(QLineEdit.EchoMode.Password)
            toggle_button.setIcon(QIcon("assets/eye-closed.png"))

    def create_password_field(self, placeholder, icon_btn):
        container = QFrame()
        container.setFixedSize(300, 40)
        container.setStyleSheet("QFrame { background: transparent; }")

        line_edit = QLineEdit(container)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        line_edit.setGeometry(0, 0, 300, 40)
        line_edit.setStyleSheet(self.input_style() + "padding-right: 35px;")

        icon_btn.setParent(container)
        icon_btn.setGeometry(265, 5, 30, 30)  
        icon_btn.raise_()

        return container, line_edit


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
    window.show() 
    app.exec()