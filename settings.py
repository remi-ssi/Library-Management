#WORKING NA TO PERO UHMM INDE KO KASI ALAM PAANO AYUSIN YUNG ITSURA 
#PWEDE NIYO NAMAN NG IEDIT

import sys
from Authentication import Authentication
from navigation_sidebar import NavigationSidebar
from navbar_logic import nav_manager
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QFont, QMovie
from PySide6.QtWidgets import (
    QApplication, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout,
    QSpacerItem, QSizePolicy, QHBoxLayout, QMainWindow, QFrame, QDialog,
    QFormLayout, QMessageBox, QScrollArea
)

#The Setting inherits the QMainWindow
class Settings(QMainWindow): 
    def __init__(self):
        super().__init__() #GIVEN NA TO EVERYTIME

        self.setWindowTitle("Accounts and Settings")
          # Store user data as instance variable
        self.user_data = {
            'first_name': 'Reymie',
            'middle_name': 'Lovete',
            'last_name': 'Gonzaga',
            'email': 'reymiereymireyjfaidfnkauhdfkushfkds@gmail.com',
            'password': 'badette'  # Default password 
        }
        
        self.setup_ui()
        self.showMaximized()

    def setup_ui(self):
        # Main widget and layout WITH sidebar
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Use QHBoxLayout for sidebar + content layout 
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  
        main_layout.setSpacing(0)

       
        self.sidebar = NavigationSidebar()
        self.sidebar.on_navigation_clicked = nav_manager.handle_navigation
        main_layout.addWidget(self.sidebar)        
        
        # Create scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f1efe3;
            }
            QScrollBar:vertical {
                background-color: #f1efe3;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #f1efe3;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #e0ddd1;
            }
        """)
        
        # Create content widget for the scroll area
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f1efe3;")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 20, 40, 20) 
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Align everything to top
        
        # Header - just a label
        header = self.create_header()
        content_layout.addWidget(header)        # Personal Info Section (title + container) - store reference for updates
        self.personal_info_section = self.create_personal_info_section()
        content_layout.addWidget(self.personal_info_section)
          # Change Password Section
        change_password_section = self.create_change_password_section()
        content_layout.addWidget(change_password_section)
          # About Us Section
        about_us_section = self.create_about_us_section()
        content_layout.addWidget(about_us_section)

          # Info Containers Section (Contact Number and App Version)
        info_containers_section = self.create_info_containers_section()
        content_layout.addWidget(info_containers_section)
        
        # Logout Button Section
        logout_section = self.create_logout_section()
        content_layout.addWidget(logout_section)
        
        # Store content layout reference for updates
        self.content_layout = content_layout
        
        # Add stretch to push everything to the top
        content_layout.addStretch()
        
        # Set the content widget to the scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to main layout
        main_layout.addWidget(scroll_area)

    def create_header(self):
        # Just a label, no QFrame
        label = QLabel("Account and Settings")
        font = QFont("Times New Roman", 35, QFont.Bold)
        label.setFont(font)
        label.setContentsMargins(40, 90, 40, 20)
        label.setAlignment(Qt.AlignmentFlag.AlignTop) 
        label.setStyleSheet("color:#714423; border: none;")
        
        return label

    def create_personal_info_section(self):
        # Main section widget that contains both title and container
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #f1efe3;")
        
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(15)
        
        # Title - OUTSIDE the container
        title_label = QLabel("PERSONAL INFO")
        title_label.setFont(QFont("Times New Roman", 18, QFont.Bold))
        title_label.setContentsMargins(40, 20, 0, 0)
        title_label.setStyleSheet("color: #5C4033; border: none; background-color: transparent;")
        section_layout.addWidget(title_label)
        
        # Container for the actual personal info
        container = self.create_personal_info_container()
        section_layout.addWidget(container)
        
        return section_widget

    def create_personal_info_container(self):
        # Main container widget
        container = QWidget()
        container.setFixedHeight(200)
        container.setStyleSheet("""
            QWidget {
                background-color: #f5f3e7;
                border: 3px solid #714423;
                border-radius: 25px;
                margin: 0px 20px;
            }
        """)
        
        # Main layout for the container
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(0)
        
        # Horizontal layout for content: Left (info) + Right (edit button)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)  
        
        # Left container - Personal information
        info_container = QWidget()
        info_container.setStyleSheet("background-color: transparent; border: none;")
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)
        
        # Use instance user data
        user_data = self.user_data
        
        # Field mapping for display (easy to modify labels without changing data structure)
        field_labels = {
            'first_name': 'First Name:',
            'middle_name': 'Middle Name:',
            'last_name': 'Last Name:',
            'email': 'Email:'
        }
        
        # Create the display fields
        for field_key, field_label in field_labels.items():
            field_value = user_data.get(field_key, 'N/A')  # Get value or default to 'N/A'
            # Create horizontal layout for each field
            field_layout = QHBoxLayout()
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(10)
            
            # Field name label (e.g., "First Name:")
            field_name_label = QLabel(field_label)
            field_name_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
            field_name_label.setStyleSheet("""
                QLabel {
                    color: #5C4033; 
                    border: none; 
                    background-color: transparent;
                    padding: 2px 0px;
                }
            """)
            field_name_label.setFixedWidth(160)
            field_name_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Field value label (e.g., "John")
            value_label = QLabel(field_value)
            value_label.setFont(QFont("Times New Roman", 14))
            value_label.setStyleSheet("""
                QLabel {
                    color: #333333; 
                    border: none; 
                    background-color: transparent;
                    padding: 2px 0px;
                }
            """)
            value_label.setWordWrap(True)  # Enable word wrapping for long text
            value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            field_layout.addWidget(field_name_label)
            field_layout.addWidget(value_label)
            field_layout.addStretch()
            
            info_layout.addLayout(field_layout)
        
        # Right container - Edit button
        button_container = QWidget()
        button_container.setStyleSheet("background-color: transparent; border: none;")
        button_container.setFixedWidth(180) 
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Edit button (maroon/red with pen emoji)
        edit_btn = QPushButton("✏️ Edit")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #c00;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
                font-family: 'Times New Roman';
            }
            QPushButton:hover {
                background-color: #ff0606;
            }
            QPushButton:pressed {
                background-color: #ff0606;
            }        """)
        edit_btn.setFixedSize(150, 45)
        edit_btn.clicked.connect(self.open_edit_dialog)  # Connect to edit dialog method
        button_layout.addWidget(edit_btn)
        
        # Add both containers to horizontal layout
        content_layout.addWidget(info_container)
        content_layout.addWidget(button_container)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout)
        
        return container

    def open_edit_dialog(self):
        """Open the edit personal information dialog"""
        # Open the dialog with current user data
        dialog = EditPersonalInfoDialog(self.user_data, self)
        
        if dialog.exec() == QDialog.Accepted:
            # Get the updated data
            updated_data = dialog.get_updated_data()
            
            # Update the display (refresh the personal info container)
            self.update_personal_info_display(updated_data)
            
            # Show success message
            QMessageBox.information(self, "Success", 
                                  f"Personal information updated successfully!\n\n"
                                  f"Name: {updated_data['first_name']} {updated_data['middle_name']} {updated_data['last_name']}\n"
                                  f"Email: {updated_data['email']}")

    def update_personal_info_display(self, updated_data):
        """Update the personal info display with new data"""
        # Update the instance data
        self.user_data = updated_data
        
        # Remove the old personal info section
        self.content_layout.removeWidget(self.personal_info_section)
        self.personal_info_section.deleteLater()
        
        # Create and add the new personal info section with updated data
        self.personal_info_section = self.create_personal_info_section()
        self.content_layout.insertWidget(1, self.personal_info_section)  # Insert after header (index 1)
        
        print(f"Updated user data: {updated_data}")
        

    def create_change_password_section(self):
        # Main section widget that contains the change password container
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #f1efe3;")
        
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 18, 0, 0)  # Remove extra margins
        section_layout.setSpacing(0)
        
        # Container for the change password - make it clickable like a button
        container = self.create_change_password_container()
        section_layout.addWidget(container)
        
        return section_widget

    def create_change_password_container(self):
        # Main container widget that acts like a button
        container = QPushButton() 
        container.setFixedHeight(80)  
        container.setCursor(Qt.CursorShape.PointingHandCursor)  
        container.setStyleSheet("""
            QPushButton {
                background-color: #714423;
                border: 3px solid #714423;
                border-radius: 20px;
                margin: 0px 20px;
                text-align: left;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #8a5429;
                border: 3px solid #8a5429;
            }
            QPushButton:pressed {
                background-color: #5d3a1e;
                border: 3px solid #5d3a1e;            }
        """)
        
        # Create layout for the button content
        content_layout = QHBoxLayout(container)
        content_layout.setContentsMargins(25, 15, 25, 15)
        content_layout.setSpacing(20)
        
        # Left side - Icon and text
    
        left_layout = QHBoxLayout()
        left_layout.setSpacing(15)
        
        # Lock icon
        icon_label = QLabel("🔒")
        icon_label.setFont(QFont("Times New Roman", 20))
        icon_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Text
        text_label = QLabel("Change Password")
        text_label.setFont(QFont("Times New Roman", 16, QFont.Bold))
        text_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        left_layout.addSpacing(20)  # Add some space before the icon
        left_layout.addWidget(icon_label)
        left_layout.addWidget(text_label)
        left_layout.addStretch()
        
        # Right side - Arrow indicator
        arrow_label = QLabel("→")
        arrow_label.setFont(QFont("Times New Roman", 18, QFont.Bold))
        arrow_label.setContentsMargins(0, 0, 30, 0)  # Right margin for arrow
        arrow_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addLayout(left_layout)
        content_layout.addWidget(arrow_label)
        
        
        # Connect click event
        container.clicked.connect(self.open_change_password_dialog)        
        return container

    def open_change_password_dialog(self):
        """Open the change password dialog"""        # First dialog: Verify current password
        current_password_dialog = CurrentPasswordDialog(self.user_data.get('password', ''), self)
        if current_password_dialog.exec() == QDialog.DialogCode.Accepted:
            # If current password is correct, open new password dialog
            current_password = self.user_data.get('password', '')
            new_password_dialog = NewPasswordDialog(current_password, self)
            if new_password_dialog.exec() == QDialog.DialogCode.Accepted:
                # Update the password in user data
                new_password = new_password_dialog.get_new_password()
                self.user_data['password'] = new_password
                QMessageBox.information(self, "Success", "Password changed successfully!")

    def create_about_us_section(self):
        # Main section widget that contains the about us container
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #f1efe3;")
        
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 13, 0, 0)  # Remove extra margins
        section_layout.setSpacing(0)
        
        # Container for the about us - make it clickable like a button
        container = self.create_about_us_container()
        section_layout.addWidget(container)
        
        return section_widget

    def create_about_us_container(self):
        # Main container widget that acts like a button
        container = QPushButton()
        container.setFixedHeight(80)
        container.setCursor(Qt.CursorShape.PointingHandCursor)
        container.setStyleSheet("""
            QPushButton {
                background-color: #714423;
                border: 3px solid #714423;
                border-radius: 20px;
                margin: 0px 20px;
                text-align: left;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #8a5429;
                border: 3px solid #8a5429;
            }
            QPushButton:pressed {
                background-color: #5d3a1e;
                border: 3px solid #5d3a1e;
            }
        """)
        
        # Create layout for the button content
        content_layout = QHBoxLayout(container)
        content_layout.setContentsMargins(25, 15, 25, 15)
        content_layout.setSpacing(20)
        
        # Left side - Icon and text
        left_layout = QHBoxLayout()
        left_layout.setSpacing(15)
        
        # Info icon
        icon_label = QLabel("ℹ️")
        icon_label.setFont(QFont("Times New Roman", 20))
        icon_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Text
        text_label = QLabel("About Us")
        text_label.setFont(QFont("Times New Roman", 16, QFont.Bold))
        text_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        left_layout.addSpacing(20)  # Add some space before the icon
        left_layout.addWidget(icon_label)
        left_layout.addWidget(text_label)
        left_layout.addStretch()
        
        # Right side - Arrow indicator
        arrow_label = QLabel("→")
        arrow_label.setFont(QFont("Times New Roman", 18, QFont.Bold))
        arrow_label.setContentsMargins(0, 0, 30, 0)  # Right margin for arrow
        arrow_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout.addLayout(left_layout)
        content_layout.addWidget(arrow_label)
        
        # Connect click event
        container.clicked.connect(self.open_about_us_dialog)
        
        return container

    def open_about_us_dialog(self):
        """Open the about us dialog"""
        about_dialog = AboutUsDialog(self)
        about_dialog.exec()
        
    def create_info_containers_section(self):
        # Main section widget that contains the info containers
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #f1efe3;")
        
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 15, 0, 0)  # Remove extra margins
        section_layout.setSpacing(0)
        
        # Horizontal layout for the two containers
        containers_layout = QHBoxLayout()
        containers_layout.setContentsMargins(20, 0, 20, 0)
        containers_layout.setSpacing(15)
        
        # Left container - Contact Number
        contact_container = self.create_info_container("📞", "Contact Number", "+1 (555) 123-4567")
        containers_layout.addWidget(contact_container)
        
        containers_layout.addSpacing(35)
        # Right container - App Version
        version_container = self.create_info_container("📱", "App Version", "v1.0.0")
        containers_layout.addWidget(version_container)
        
        section_layout.addLayout(containers_layout)
        
        return section_widget

    def create_info_container(self, icon, title, info):
        # Main container widget
        container = QWidget()
        container.setFixedHeight(80)
        container.setStyleSheet("""
            QWidget {
                background-color: #f1efe3;
                border: 3px solid #714423;
                border-radius: 15px;
            }
        """)
        
        # Main horizontal layout for the container
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Times New Roman", 16))
        icon_label.setStyleSheet("color: #714423; background-color: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title (bold) - same font size as personal info fields
        title_label = QLabel(f"{title}:")
        title_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        title_label.setStyleSheet("color: #5C4033; background-color: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        # Info (not bold) - same font size as personal info fields
        info_label = QLabel(info)
        info_label.setFont(QFont("Times New Roman", 14))
        info_label.setStyleSheet("color: #333333; background-color: transparent; border: none;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        main_layout.addWidget(icon_label)
        main_layout.addWidget(title_label)
        main_layout.addWidget(info_label)
        main_layout.addStretch()
        
        return container
    
    
    def create_logout_section(self):
        # Main section widget that contains the logout button
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #f1efe3;")
        
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)  # Remove extra margins
        section_layout.setSpacing(0)
        
        # Horizontal layout to position button on the right
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 50, 20, 10)
        button_layout.setSpacing(0)
        
        # Add stretch to push button to the right
        button_layout.addStretch()
          # Logout button (small, red)
        logout_button = QPushButton("Logout")
        logout_button.setFixedSize(120, 40)
        logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 8px;
                font-family: 'Times New Roman';
                font-size: 15px;
                font-weight: bold;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        
        # Connect logout functionality
        logout_button.clicked.connect(self.handle_logout)
        
        button_layout.addWidget(logout_button)
        section_layout.addLayout(button_layout)
        
        return section_widget
    
    def handle_logout(self):
        """Handle logout functionality"""
        reply = QMessageBox.question(
            self, 
            "Logout Confirmation", 
            "Are you sure you want to logout?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Close the current window and return to login or main menu
            self.close()
            QMessageBox.information(self, "Logged Out", "You have been logged out successfully!")
            self.auth_window = Authentication()  # use correct variable and class
            self.auth_window.show()


class EditPersonalInfoDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.user_data = user_data.copy()  # Copy of the original data
        self.updated_data = user_data.copy()  # Data to be modified
        
        self.setWindowTitle("Edit Personal Information")
        self.setFixedSize(450, 400)
        self.setModal(True)
        
        # Apply styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
                font-family: 'Times New Roman';
            }
            QLabel {
                color: #5C4033;
                font-weight: bold;
                font-size: 14px;
                border: none;
            }
            QLineEdit {
                background-color: white;
                border: 2px solid #d4c5a9;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                color: #333;
                font-family: 'Times New Roman';
            }
            QLineEdit:focus {
                border-color: #5C4033;
            }
            QPushButton {
                font-family: 'Times New Roman';
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title = QLabel("Edit Personal Information")
        title.setFont(QFont("Times New Roman", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #5C4033; font: 20px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form layout for input fields
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        
        # Create input fields with pre-filled data
        self.first_name_input = QLineEdit()
        self.first_name_input.setText(self.user_data.get('first_name', ''))
        self.first_name_input.setPlaceholderText("Enter first name")
        
        self.middle_name_input = QLineEdit()
        self.middle_name_input.setText(self.user_data.get('middle_name', ''))
        self.middle_name_input.setPlaceholderText("Enter middle name")
        
        self.last_name_input = QLineEdit()
        self.last_name_input.setText(self.user_data.get('last_name', ''))
        self.last_name_input.setPlaceholderText("Enter last name")
        
        self.email_input = QLineEdit()
        self.email_input.setText(self.user_data.get('email', ''))
        self.email_input.setPlaceholderText("Enter email address")
        
        # Add fields to form
        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Middle Name:", self.middle_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Email:", self.email_input)
        
        layout.addLayout(form_layout)
        
        # Add some space
        layout.addSpacing(20)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b4513;
                color: white;
                border: none;
            }
            QPushButton:hover {
                background-color: #7a3d0f;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
    def save_changes(self):
        # Validate that fields are not empty
        if not self.first_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "First name is required!")
            return
            
        if not self.last_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Last name is required!")
            return
            
        if not self.email_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Email is required!")
            return
        
        # Update the data
        self.updated_data = {
            'first_name': self.first_name_input.text().strip(),
            'middle_name': self.middle_name_input.text().strip(),
            'last_name': self.last_name_input.text().strip(),
            'email': self.email_input.text().strip()
        }
        
        # Accept the dialog
        self.accept()
        
    def get_updated_data(self):
        return self.updated_data



class CurrentPasswordDialog(QDialog):
    def __init__(self, correct_password, parent=None):
        super().__init__(parent)
        self.correct_password = correct_password
        
        self.setWindowTitle("Verify Current Password")
        self.setFixedSize(400, 250)  
        self.setModal(True)
        
       
        self.setStyleSheet("""            QDialog {
                background-color: #f1efe3;
                border-radius: 10px;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        # Add some stretch at the top
        layout.addStretch(1)
        
        # Title
        title_label = QLabel("Enter Current Password")
        title_label.setFont(QFont("Times New Roman", 16, QFont.Bold))
        title_label.setStyleSheet("color: #5C4033; background-color: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Add some space after title
        layout.addSpacing(15)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(QFont("Times New Roman", 12))
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #714423;
                border-radius: 5px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #8a5429;
            }
        """)
        self.password_input.setPlaceholderText("Enter your current password")
        layout.addWidget(self.password_input)
        
        # Error label (initially hidden) - with fixed height to maintain layout
        self.error_label = QLabel("Incorrect password. Please try again.")
        self.error_label.setFont(QFont("Times New Roman", 11))
        self.error_label.setStyleSheet("color: #d32f2f; background-color: transparent; border: none;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setFixedHeight(20)  # Fixed height to reserve space
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Add stretch before buttons to push them down
        layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Times New Roman", 12))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        verify_btn = QPushButton("Verify")
        verify_btn.setFont(QFont("Times New Roman", 12))
        verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #714423;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8a5429;
            }
        """)
        verify_btn.clicked.connect(self.verify_password)
        verify_btn.setDefault(True)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(verify_btn)
        layout.addLayout(button_layout)
        
        # Connect Enter key to verify
        self.password_input.returnPressed.connect(self.verify_password)
        
    def verify_password(self):
        entered_password = self.password_input.text()
        if entered_password == self.correct_password:
            self.accept()
        else:
            self.error_label.show()
            self.password_input.clear()
            self.password_input.setFocus()


class NewPasswordDialog(QDialog):
    def __init__(self, current_password, parent=None):
        super().__init__(parent)
        self.current_password = current_password
        self.new_password = ""
        
        self.setWindowTitle("Set New Password")
        self.setFixedSize(450, 350)
        self.setModal(True)
        
        # Apply styling similar to EditPersonalInfoDialog
        self.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
                border-radius: 10px;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        
        # Add some stretch at the top
        layout.addStretch(1)
        
        # Title
        title_label = QLabel("Create New Password")
        title_label.setFont(QFont("Times New Roman", 16, QFont.Bold))
        title_label.setStyleSheet("color: #5C4033; background-color: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Add some space after title
        layout.addSpacing(15)
        
        # Form layout for password fields
        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        
        # New password
        new_pwd_label = QLabel("New Password:")
        new_pwd_label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        new_pwd_label.setStyleSheet("color: #5C4033; background-color: transparent; border: none;")
        form_layout.addWidget(new_pwd_label)
        
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setFont(QFont("Times New Roman", 12))
        self.new_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #714423;
                border-radius: 5px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #8a5429;
            }
        """)
        self.new_password_input.setPlaceholderText("Enter new password")
        form_layout.addWidget(self.new_password_input)
        
        # Confirm password
        confirm_pwd_label = QLabel("Confirm New Password:")
        confirm_pwd_label.setFont(QFont("Times New Roman", 12, QFont.Bold))
        confirm_pwd_label.setStyleSheet("color: #5C4033; background-color: transparent; border: none;")
        form_layout.addWidget(confirm_pwd_label)
        
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setFont(QFont("Times New Roman", 12))
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #714423;
                border-radius: 5px;
                background-color: white;
                color: #333;
            }
            QLineEdit:focus {
                border: 2px solid #8a5429;
            }
        """)
        self.confirm_password_input.setPlaceholderText("Confirm new password")
        form_layout.addWidget(self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Error label (initially hidden) - with fixed height to maintain layout
        self.error_label = QLabel("")
        self.error_label.setFont(QFont("Times New Roman", 11))
        self.error_label.setStyleSheet("color: #d32f2f; background-color: transparent; border: none;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setFixedHeight(20)  # Fixed height to reserve space
        self.error_label.hide()
        layout.addWidget(self.error_label)
        
        # Add stretch before buttons to push them down
        layout.addStretch(1)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Times New Roman", 12))
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Change Password")
        save_btn.setFont(QFont("Times New Roman", 12))
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #714423;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8a5429;
            }
        """)
        save_btn.clicked.connect(self.save_new_password)
        save_btn.setDefault(True)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
          # Connect Enter key to save
        self.confirm_password_input.returnPressed.connect(self.save_new_password)
        
    def save_new_password(self):
        new_password = self.new_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # Validation
        if not new_password:
            self.show_error("Please enter a new password.")
            return
            
        if len(new_password) < 6:
            self.show_error("Password must be at least 6 characters long.")
            return
            
        if new_password == self.current_password:
            self.show_error("New password cannot be the same as current password.")
            return
            
        if new_password != confirm_password:
            self.show_error("Passwords do not match. Please try again.")
            return
        
        # Save the new password
        self.new_password = new_password
        self.accept()
        
    def show_error(self, message):
        self.error_label.setText(message)
        self.error_label.show()
        
    def get_new_password(self):
        return self.new_password
        


class AboutUsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("About Us")
        self.setFixedSize(600, 400)  
        self.setModal(True)
        
       
        self.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
                border-radius: 10px;
            }
        """)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("BJRS Library Management System")
        title_label.setFont(QFont("Times New Roman", 20, QFont.Bold))
        title_label.setStyleSheet("color: #5C4033; background-color: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("About Our Application")
        subtitle_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        subtitle_label.setStyleSheet("color: #714423; background-color: transparent; border: none;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Description text
        description_text = QLabel("""
        Welcome to our Library Management System!
        
        This app is ano eh tanong niyo si Nads
        
        Features:
        • im hungry
        • sanaol nagreview sa FE2
        • so sleepyy
        • JasMinE QtQt
        
        ADVANCE HAPPY BIRTHDAY REYMIE!!!
        Developed with ❤️ using Python and PySide6
        
        Thank you for using our Library Management System!
        """)
        description_text.setFont(QFont("Times New Roman", 12))
        description_text.setStyleSheet("color: #333333; background-color: transparent; border: none; line-height: 1.4;")
        description_text.setWordWrap(True)
        description_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(description_text)
        
        # Add stretch to push button to bottom
        layout.addStretch()
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: Green;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ab41;
            }
            QPushButton:pressed {
                background-color: #00ab41;
            }
        """)
        close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        


if __name__ == "__main__":
    #This runs the program
    app = QApplication(sys.argv)

    # Initialize navigation manager
    nav_manager.initialize(app)

    default_font = QFont("Times New Roman")
    app.setFont(default_font)
    app.setStyleSheet("""
        QLabel {color: #5C4033}         
    """)

    window = Settings()
    nav_manager._current_window = window
    window.show() 
    app.exec()