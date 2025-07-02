from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QFrame, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon
import re
import bcrypt

class ResetPasswordDialog(QDialog):
    def __init__(self, email, otp=None, db_seeder=None, parent=None, is_change_password=False):
        super().__init__(parent)
        self.email = email
        self.otp = otp
        self.db_seeder = db_seeder
        self.is_change_password = is_change_password  # Flag to determine if it's change password from settings

        # Set title and image based on the mode
        if self.is_change_password:
            self.setWindowTitle("Change Your Password")
            title_text = "Change Your Password"
            button_text = "Change Password"
        else:
            self.setWindowTitle("Reset Your Password")
            title_text = "Reset Your Password"
            button_text = "Reset Password"

        self.setFixedSize(500, 550 if self.is_change_password else 500)  # Slightly taller for change password
        self.setStyleSheet("background-color: #f1efe3; border-radius: 16px;")

        # Current password field (only for change password)
        if self.is_change_password:
            self.toggle_current_pass_btn = QPushButton()
            self.toggle_current_pass_btn.setIcon(QIcon("assets/eye-closed.png"))
            self.toggle_current_pass_btn.setFixedSize(30, 30)
            self.toggle_current_pass_btn.setStyleSheet("border: none; background: transparent;")
            self.toggle_current_pass_btn.clicked.connect(self.toggle_current_password_visibility)
            
            current_pass_container, self.current_password_input = self.create_password_field("Enter current password", self.toggle_current_pass_btn)

        # New password field
        self.toggle_new_pass_btn = QPushButton()
        self.toggle_new_pass_btn.setIcon(QIcon("assets/eye-closed.png"))
        self.toggle_new_pass_btn.setFixedSize(30, 30)
        self.toggle_new_pass_btn.setStyleSheet("border: none; background: transparent;")
        self.toggle_new_pass_btn.clicked.connect(self.toggle_new_password_visibility)

        new_pass_container, self.new_password_input = self.create_password_field("Enter new password", self.toggle_new_pass_btn)

        # Confirm password field
        self.toggle_confirm_pass_btn = QPushButton()
        self.toggle_confirm_pass_btn.setIcon(QIcon("assets/eye-closed.png"))
        self.toggle_confirm_pass_btn.setFixedSize(30, 30)
        self.toggle_confirm_pass_btn.setStyleSheet("border: none; background: transparent;")
        self.toggle_confirm_pass_btn.clicked.connect(self.toggle_confirm_password_visibility)

        confirm_pass_container, self.confirm_password_input = self.create_password_field("Confirm new password", self.toggle_confirm_pass_btn)

        self.message_label = QLabel("")
        self.message_label.setStyleSheet("color: red; font-weight: bold;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.hide()

        self.reset_button = QPushButton(button_text)
        self.reset_button.setFixedHeight(40)
        self.reset_button.setFixedWidth(200)
        self.reset_button.setStyleSheet("""
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
        self.reset_button.clicked.connect(self.process_password_change)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)

        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #714423;")

        layout.addWidget(title)
        layout.addSpacing(20)
        
        # Add the appropriate image
        image_label = QLabel()
        if self.is_change_password:
            image_label.setPixmap(QIcon("assets/changepass.png").pixmap(120, 120))  
        else:
            image_label.setPixmap(QIcon("assets/changepass.png").pixmap(150, 150))
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(image_label)
        layout.addSpacing(15)
        
        # Add current password field if it's change password mode
        if self.is_change_password:
            layout.addWidget(current_pass_container, alignment=Qt.AlignmentFlag.AlignHCenter)
            layout.addSpacing(10)
        
        # Add new password and confirm password fields
        layout.addWidget(new_pass_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(10)
        layout.addWidget(confirm_pass_container, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(10)
        
        layout.addWidget(self.message_label)
        layout.addWidget(self.reset_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.setLayout(layout)

    def input_style(self):
        return """
            QLineEdit {
                border: 2px solid #B7966B;
                border-radius: 10px;
                padding: 8px;
                font-size: 16px;
                background-color: #F0ECE9;
                color: #4A4947;
            }
            QLineEdit:focus {
                border: 3px solid #714423;
            }
        """

    def toggle_current_password_visibility(self):
        if self.current_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.current_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_current_pass_btn.setIcon(QIcon("assets/eye-open.png"))
        else:
            self.current_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_current_pass_btn.setIcon(QIcon("assets/eye-closed.png"))

    def toggle_new_password_visibility(self):
        if self.new_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.new_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_new_pass_btn.setIcon(QIcon("assets/eye-open.png"))
        else:
            self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_new_pass_btn.setIcon(QIcon("assets/eye-closed.png"))

    def toggle_confirm_password_visibility(self):
        if self.confirm_password_input.echoMode() == QLineEdit.EchoMode.Password:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_confirm_pass_btn.setIcon(QIcon("assets/eye-open.png"))
        else:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_confirm_pass_btn.setIcon(QIcon("assets/eye-closed.png"))

    def process_password_change(self):
        # Get current password if in change password mode
        if self.is_change_password:
            current_password = self.current_password_input.text().strip()
            if not current_password:
                self.show_error("Please enter your current password.")
                return
            
            # TODO: Verify current password against database
            # You'll need to implement this method in your db_seeder
            if not self.db_seeder.verify_current_password(self.email, current_password):
                self.show_error("Current password is incorrect.")
                return

        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()

        # Validate new password
        if len(new_password) < 8:
            self.show_error("Password must be at least 8 characters.")
            return
        if not re.search(r"[A-Z]", new_password):
            self.show_error("Include at least one uppercase letter.")
            return
        if not re.search(r"[a-z]", new_password):
            self.show_error("Include at least one lowercase letter.")
            return
        if not re.search(r"\d", new_password):
            self.show_error("Include at least one digit.")
            return
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", new_password):
            self.show_error("Include at least one special character.")
            return
        if new_password != confirm_password:
            self.show_error("Passwords do not match.")
            return

        # Try to change the password
        try:
            if self.db_seeder.changePassword(self.email, new_password):
                if self.is_change_password:
                    self.show_success("You've successfully changed your password.")
                else:
                    self.show_success("You've successfully reset your password.")
                
                # Close the dialog after showing success message for 2 seconds
                QTimer.singleShot(2000, self.close_and_return)
            else:
                self.show_error("Failed to update password. Please try again.")
        except Exception as e:
            self.show_error(f"Error: {str(e)}")

    def show_error(self, message):
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: red; font-weight: bold;")
        self.message_label.show()

    def show_success(self, message):
        self.message_label.setText(message)
        self.message_label.setStyleSheet("color: green; font-weight: bold;")
        self.message_label.show()

    def close_and_return(self):
        self.close()
        
        if self.is_change_password:
            # For change password, redirect to login for security
            if hasattr(self.parent(), 'logout_and_show_login'):
                self.parent().logout_and_show_login()
            else:
                # Fallback: close parent and try to find login window
                self.parent().close()
                # You might need to emit a signal or call a specific method to show login
                # This depends on your app structure
        else:
            # For reset password, show the login window
            if self.parent():
                self.parent().show()

    def create_password_field(self, placeholder, icon_btn):
        container = QFrame()
        container.setFixedSize(350, 50)
        container.setStyleSheet("QFrame { background: transparent; }")

        line_edit = QLineEdit(container)
        line_edit.setPlaceholderText(placeholder)
        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
        line_edit.setGeometry(0, 5, 350, 40)
        line_edit.setStyleSheet(self.input_style() + "padding-right: 40px;")

        icon_btn.setParent(container)
        icon_btn.setGeometry(315, 10, 30, 30)
        icon_btn.raise_()

        return container, line_edit