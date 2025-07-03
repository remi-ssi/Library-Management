import sys
import re
from tryDatabase import DatabaseSeeder
from Authentication import Authentication
from navigation_sidebar import NavigationSidebar
from navbar_logic import nav_manager
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QLineEdit, QLabel, QPushButton, QWidget, QVBoxLayout,
    QSpacerItem, QSizePolicy, QHBoxLayout, QMainWindow, QScrollArea, QDialog,
    QFormLayout, QMessageBox
)

class Settings(QMainWindow):
    def __init__(self, librarian_id=1):  # Default librarian_id for testing
        super().__init__()
        self.db_seeder = DatabaseSeeder()
        self.librarian_id = librarian_id  # Store librarian_id
        self.user_data = self.load_user_data()
        self.personal_info_labels = {}
        self.setWindowTitle("Accounts and Settings")
        self.setStyleSheet("""
            Settings {
                background-color: #f1efe3;
            }
        """)
        self.setup_ui()
        self.showMaximized()

    def load_user_data(self):
        """Load user data from the database for the given librarian_id."""
        try:
            print(f"🔍 Loading user data for librarian_id: {self.librarian_id}")
            
            # Use existing get_all_records method to get all librarians
            librarians = self.db_seeder.get_all_records(tableName="Librarian", id= self.librarian_id)
            
            # Find the librarian with matching LibrarianID
            librarian = None
            for lib in librarians:
                if lib.get('LibrarianID') == self.librarian_id:
                    librarian = lib
                    break
            
            if librarian:
                print(f"✅ Found librarian: {librarian.get('LibUsername')}")
                return {
                    'first_name': librarian.get('FName', 'N/A'),
                    'middle_name': librarian.get('MName', '') or '',
                    'last_name': librarian.get('LName', 'N/A'),
                    'email': librarian.get('LibUsername', 'N/A')
                }
            else:
                print(f"❌ Librarian not found with ID: {self.librarian_id}")
                print(f"📊 Available librarian IDs: {[lib.get('LibrarianID') for lib in librarians]}")
                QMessageBox.critical(self, "Error", f"Librarian not found in database (ID: {self.librarian_id}).")
                return {
                    'first_name': 'N/A',
                    'middle_name': '',
                    'last_name': 'N/A',
                    'email': 'N/A'
                }
                
        except Exception as e:
            print(f"❌ Error loading user data: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Database Error", f"Failed to load user data: {str(e)}")
            return {
                'first_name': 'N/A',
                'middle_name': '',
                'last_name': 'N/A',
                'email': 'N/A'
            }
    def open_edit_dialog(self):
        """Open the edit personal information dialog"""
        dialog = EditPersonalInfoDialog(self.user_data, self.librarian_id, self)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_updated_data()
            self.update_personal_info_display(updated_data)
            full_name = f"{updated_data['first_name']} {updated_data['middle_name']} {updated_data['last_name']}".strip()
            QMessageBox.information(self, "Success",
                                    f"Personal information updated successfully!\n\n"
                                    f"Name: {full_name}\n"
                                    f"Email: {updated_data['email']}")

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.sidebar = NavigationSidebar()
        self.sidebar.on_navigation_clicked = nav_manager.handle_navigation
        main_layout.addWidget(self.sidebar)

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

        # Create a main container that will hold content and footer
        main_container = QWidget()
        main_container.setStyleSheet("background-color: #f5f3ed;")
        main_container_layout = QVBoxLayout(main_container)
        main_container_layout.setContentsMargins(0, 0, 0, 0)
        main_container_layout.setSpacing(0)
        
        # Create content widget with margins
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: #f5f3ed;")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 20, 40, 20)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)


        # Add all your content widgets
        header = self.create_header()
        content_layout.addWidget(header)

        self.personal_info_section = self.create_personal_info_section()
        content_layout.addWidget(self.personal_info_section)

        about_us_section = self.create_about_us_section()
        content_layout.addWidget(about_us_section)

        # Add Logout section (centered)
        logout_section = self.create_logout_section()
        content_layout.addWidget(logout_section)


        # Stretch to push content to top
        content_layout.addStretch()
        
        # Add content to main container
        main_container_layout.addWidget(content_widget, 1)  # 1 = stretch factor
        
        # Add footer to main container (without margins)
        footer = self.create_footer()
        main_container_layout.addWidget(footer)
        
        # Set the main container as the widget for scroll area
        scroll_area.setWidget(main_container)
        main_layout.addWidget(scroll_area)

    def create_header(self):
        label = QLabel("Account and Settings")
        font = QFont("Times New Roman", 35, QFont.Bold)
        label.setFont(font)
        label.setContentsMargins(40, 90, 40, 20)
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        label.setStyleSheet("color:#714423; border: none;")
        return label

    def create_personal_info_section(self):
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #f5f3ed;")
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 0, 0, 0)
        section_layout.setSpacing(0)

        # Header + Edit button on top
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(40, 20, 40, 10)
        header_layout.setSpacing(10)

        title_label = QLabel("PERSONAL INFO")
        title_label.setFont(QFont("Times New Roman", 18, QFont.Bold))
        title_label.setStyleSheet("color: #5C4033; border: none; background-color: transparent;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

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
        """)
        edit_btn.setFixedSize(100, 40)
        edit_btn.clicked.connect(self.open_edit_dialog)
        header_layout.addWidget(edit_btn)

        section_layout.addLayout(header_layout)
        

        # Add container with personal info + change password
        container = self.create_personal_info_container()
        section_layout.addWidget(container)

        return section_widget


    def create_personal_info_container(self):
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #f5f3ed;
                border: 3px solid #714423;
                border-radius: 25px;
                margin: 0px 20px;
            }
        """)

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(10)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(0, 0, 0, 0)

        info_container = QWidget()
        info_container.setStyleSheet("background-color: transparent; border: none;")
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(8)

        user_data = self.user_data
        field_labels = {
            'first_name': 'First Name:',
            'middle_name': 'Middle Name:',
            'last_name': 'Last Name:',
            'email': 'Email:'
        }

        for field_key, field_label in field_labels.items():
            field_value = user_data.get(field_key, 'N/A')
            field_layout = QHBoxLayout()
            field_layout.setContentsMargins(0, 0, 0, 0)
            field_layout.setSpacing(10)

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
            value_label.setWordWrap(True)
            value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            value_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.personal_info_labels[field_key] = value_label

            field_layout.addWidget(field_name_label)
            field_layout.addWidget(value_label)
            field_layout.addStretch()
            info_layout.addLayout(field_layout)

        content_layout.addWidget(info_container)
        main_layout.addLayout(content_layout)

        # Add Change Password button aligned bottom-right
        password_button_layout = QHBoxLayout()
        password_button_layout.setContentsMargins(0, 10, 0, 0)
        password_button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.change_password_btn = QPushButton("Change Password")
        self.change_password_btn.setFixedSize(180, 40)
        self.change_password_btn.setStyleSheet("""
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
        self.change_password_btn.clicked.connect(self.open_change_password_dialog)

        password_button_layout.addWidget(self.change_password_btn)
        main_layout.addLayout(password_button_layout)

        return container

    def open_edit_dialog(self):
        """Open the edit personal information dialog"""
        dialog = EditPersonalInfoDialog(self.user_data, self.librarian_id, self)
        if dialog.exec() == QDialog.Accepted:
            updated_data = dialog.get_updated_data()
            self.update_personal_info_display(updated_data)
            full_name = f"{updated_data['first_name']} {updated_data['middle_name']} {updated_data['last_name']}".strip()
            QMessageBox.information(self, "Success",
                                    f"Personal information updated successfully!\n\n"
                                    f"Name: {full_name}\n"
                                    f"Email: {updated_data['email']}")

    def update_personal_info_display(self, updated_data):
        """Update the personal info display with new data"""
        try:
            updates = {
                'FName': updated_data['first_name'],
                'MName': updated_data['middle_name'] or None,  # Handle empty middle name
                'LName': updated_data['last_name'],
                'LibUsername': updated_data['email']
            }
            self.db_seeder.update_table("Librarian", updates, "LibrarianID", self.librarian_id)
            self.user_data = updated_data
            for field_key, value_label in self.personal_info_labels.items():
                value_label.setText(updated_data.get(field_key, 'N/A'))
           # self.content_layout.removeWidget(self.personal_info_section)
            #self.personal_info_section.deleteLater()
            #self.personal_info_section = self.create_personal_info_section()
            #self.content_layout.insertWidget(1, self.personal_info_section)
            print(f"Updated user data: {updated_data}")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update personal info: {str(e)}")

    def create_about_us_section(self):
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #f5f3ed;")
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 13, 0, 0)
        section_layout.setSpacing(0)
        container = self.create_about_us_container()
        section_layout.addWidget(container)
        return section_widget

    def create_about_us_container(self):
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
        """)
        content_layout = QHBoxLayout(container)
        content_layout.setContentsMargins(25, 15, 25, 15)
        content_layout.setSpacing(20)

        left_layout = QHBoxLayout()
        left_layout.setSpacing(15)
        icon_label = QLabel("ℹ️")
        icon_label.setFont(QFont("Times New Roman", 20))
        icon_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label = QLabel("About Us")
        text_label.setFont(QFont("Times New Roman", 16, QFont.Bold))
        text_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        left_layout.addSpacing(20)
        left_layout.addWidget(icon_label)
        left_layout.addWidget(text_label)
        left_layout.addStretch()

        arrow_label = QLabel("→")
        arrow_label.setFont(QFont("Times New Roman", 18, QFont.Bold))
        arrow_label.setContentsMargins(0, 0, 30, 0)
        arrow_label.setStyleSheet("color: white; background-color: transparent; border: none;")
        arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_layout.addLayout(left_layout)
        content_layout.addWidget(arrow_label)
        container.clicked.connect(self.open_about_us_dialog)
        return container

    def open_about_us_dialog(self):
        about_dialog = AboutUsDialog(self)
        about_dialog.exec()

    def create_footer(self):
        footer = QWidget()
        footer.setStyleSheet("""
            QWidget {
                background-color: #dbcfc1;
                border-top: 2px solid #5C4033;
            }
        """)
        footer.setFixedHeight(30)
        
        # Use a horizontal layout with proper spacing
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 0, 20, 0)
        
        # Contact information
        contact_label = QLabel("📞 Contact Us: (+639)92 642 3076")
        contact_label.setFont(QFont("Times New Roman", 10))
        contact_label.setStyleSheet("color: #714423; background-color: transparent; border: none;")
        
        # Version information
        version_label = QLabel("📱 App Version: v1.0.0")
        version_label.setFont(QFont("Times New Roman", 10))
        version_label.setStyleSheet("color: #714423; background-color: transparent; border: none;")
        
        # Copyright text
        copyright_label = QLabel("© 2025 BJRS Library Management")
        copyright_label.setFont(QFont("Times New Roman", 10))
        copyright_label.setStyleSheet("color: #714423; background-color: transparent; border: none;")
        
        footer_layout.addWidget(contact_label)
        footer_layout.addStretch()
        footer_layout.addWidget(copyright_label)
        footer_layout.addStretch()
        footer_layout.addWidget(version_label)
        
        return footer

    def create_info_containers_section(self):
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #dbcfc1;")
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 15, 0, 0)
        section_layout.setSpacing(0)

        containers_layout = QHBoxLayout()
        containers_layout.setContentsMargins(20, 0, 20, 0)
        containers_layout.setSpacing(15)

        contact_container = self.create_info_container("📞", "Contact Us", "(+639)92 642 3076")
        containers_layout.addWidget(contact_container)
        containers_layout.addSpacing(35)
        version_container = self.create_info_container("📱", "App Version", "v1.0.0")
        containers_layout.addWidget(version_container)

        section_layout.addLayout(containers_layout)
        return section_widget

    def create_info_container(self, icon, title, info):
        container = QWidget()
        container.setFixedHeight(80)
        container.setStyleSheet("""
            QWidget {
                background-color: #dbcfc1;
                border-radius: 15px;
            }
        """)
        main_layout = QHBoxLayout(container)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(10)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Times New Roman", 16))
        icon_label.setStyleSheet("color: #714423; background-color: transparent; border: none;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(f"{title}:")
        title_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        title_label.setStyleSheet("color: #5C4033; background-color: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

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
        section_widget = QWidget()
        section_widget.setStyleSheet("background-color: #f5f3ed;")
        section_layout = QVBoxLayout(section_widget)
        section_layout.setContentsMargins(0, 50, 0, 10)
        section_layout.setSpacing(10)
        section_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logout_button = QPushButton("Logout")
        logout_button.setFixedSize(150, 45)
        logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 10px;
                font-family: 'Times New Roman';
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_button.clicked.connect(self.handle_logout)

        section_layout.addWidget(logout_button)
        return section_widget


    def handle_logout(self):
        reply = QMessageBox.question(
            self,
            "Logout Confirmation",
            "Would you like to logout now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.close()
            from Authentication import Authentication
            self.auth_window = Authentication()
            self.auth_window.show()

            
    def open_change_password_dialog(self):
        from ResetPasswordDialog import ResetPasswordDialog
        email = self.user_data.get('email', '')
        dialog = ResetPasswordDialog(
            email=email,
            db_seeder=self.db_seeder,
            parent=self,
            is_change_password=True
        )
        dialog.password_changed_and_logout.connect(self.handle_logout)
        dialog.exec()

    def close_and_return(self):
        self.close()

        if self.is_change_password:
            parent = self.parent()
            print("is_change_password =", self.is_change_password)
            print("Parent object =", parent)

            if parent and hasattr(parent, 'logout_and_show_login'):
                print("Calling logout_and_show_login()...")
                parent.logout_and_show_login()
            else:
                print("No parent or logout_and_show_login not found.")
        else:
            if self.parent():
                self.parent().show()



class EditPersonalInfoDialog(QDialog):
    def __init__(self, user_data, librarian_id, parent=None):
        super().__init__(parent)
        self.user_data = user_data.copy()
        self.librarian_id = librarian_id
        self.updated_data = user_data.copy()
        self.db_seeder = DatabaseSeeder()
        self.setWindowTitle("Edit Personal Information")
        self.setFixedSize(450, 400)
        self.setModal(True)
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

        title = QLabel("Edit Personal Information")
        title.setFont(QFont("Times New Roman", 18, QFont.Bold))
        title.setStyleSheet("color: #5C4033; font: 20px; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignLeft)

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
        self.email_input.setReadOnly(True)  

        form_layout.addRow("First Name:", self.first_name_input)
        form_layout.addRow("Middle Name:", self.middle_name_input)
        form_layout.addRow("Last Name:", self.last_name_input)
        form_layout.addRow("Email:", self.email_input)

        self.error_label = QLabel("")
        self.error_label.setFont(QFont("Times New Roman", 11))
        self.error_label.setStyleSheet("color: #d32f2f; background-color: transparent; border: none;")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setFixedHeight(20)
        self.error_label.hide()
        layout.addWidget(self.error_label)

        layout.addLayout(form_layout)
        layout.addSpacing(20)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

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

    def is_valid_email(self, email):
        """Validate email format using regex."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def is_valid_name(self, name):
        """Validate name contains only letters and spaces."""
        return name.replace(" ", "").isalpha()

    def show_error(self, message):
        """Show error message in the dialog."""
        self.error_label.setText(message)
        self.error_label.show()

    def save_changes(self):
        """Validate and save updated personal information."""
        first_name = self.first_name_input.text().strip()
        middle_name = self.middle_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        email = self.email_input.text().strip()

        if not first_name:
            self.show_error("First name is required!")
            return
        if not last_name:
            self.show_error("Last name is required!")
            return
        if not email:
            self.show_error("Email is required!")
            return
        if not self.is_valid_email(email):
            self.show_error("Invalid email format!")
            return
        if email != self.user_data['email'] and self.db_seeder.findUsername(email):
            self.show_error("Email already exists!")
            return
        if not self.is_valid_name(first_name):
            self.show_error("First name should only contain letters!")
            return
        if not self.is_valid_name(last_name):
            self.show_error("Last name should only contain letters!")
            return
        if middle_name and not self.is_valid_name(middle_name):
            self.show_error("Middle name should only contain letters!")
            return

        self.updated_data = {
            'first_name': first_name,
            'middle_name': middle_name,
            'last_name': last_name,
            'email': email
        }
        self.accept()

    def get_updated_data(self):
        return self.updated_data

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

        title_label = QLabel("BJRS Library Management System")
        title_label.setFont(QFont("Times New Roman", 20, QFont.Bold))
        title_label.setStyleSheet("color: #5C4033; background-color: transparent; border: none;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle_label = QLabel("About Our Application")
        subtitle_label.setFont(QFont("Times New Roman", 14, QFont.Bold))
        subtitle_label.setStyleSheet("color: #714423; background-color: transparent; border: none;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)

        description_text = QLabel("""
        Welcome to our Library Management System!

        This app is designed to streamline library operations, making it easy to manage books, users, and more.

        Features:
        • User-friendly interface
        • Efficient book management
        • Profile customization
        • Secure data handling

        Developed with ❤️ using Python and PySide6

        Thank you for using our Library Management System!
        """)
        description_text.setFont(QFont("Times New Roman", 12))
        description_text.setStyleSheet("color: #333333; background-color: transparent; border: none; line-height: 1.4;")
        description_text.setWordWrap(True)
        description_text.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(description_text)

        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.setFont(QFont("Times New Roman", 12, QFont.Bold))
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #008000;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ab41;
            }
        """)
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    nav_manager.initialize(app)
    default_font = QFont("Times New Roman")
    app.setFont(default_font)
    app.setStyleSheet("""
        QLabel {color: #5C4033}
    """)
    window = Settings(librarian_id=1)  # Pass a test librarian_id
    nav_manager._current_window = window
    window.show()
    app.exec()