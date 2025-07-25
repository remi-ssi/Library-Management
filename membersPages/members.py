import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QPainterPath, QFontMetrics
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QGridLayout,
    QDialog, QFormLayout, QMessageBox
)

# Import the reusable navigation sidebar
from navigation_sidebar import NavigationSidebar
from navbar_logic import nav_manager

# Connect to database seeder 
from tryDatabase import DatabaseSeeder


class ProtectedContactLineEdit(QLineEdit):
    # This is a special text box po for phone numbers. 
    # It always starts with '09' and only lets you type 11 digits.
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("09")
        self.setCursorPosition(2)
        self.textChanged.connect(self.on_text_changed)
    
    def keyPressEvent(self, event):
        # Don't let the user erase the '09' at the beginning
        cursor_pos = self.cursorPosition()
        
        if event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
            if cursor_pos <= 2:
                return
        
        super().keyPressEvent(event)
    
    def on_text_changed(self, text):
        # Every time the text changes, check if it still starts with '09' and isn't too long
        if not text.startswith("09"):
            self.blockSignals(True)
            digits_only = ''.join(filter(str.isdigit, text))
            if digits_only.startswith("09"):
                clean_text = digits_only[:11]
            else:
                remaining_digits = digits_only[2:] if digits_only.startswith("9") else digits_only
                clean_text = "09" + remaining_digits[:9]
            
            self.setText(clean_text)
            self.setCursorPosition(len(clean_text))
            self.blockSignals(False)
        
        elif len(text) > 11:
            self.blockSignals(True)
            self.setText(text[:11])
            self.blockSignals(False)

class AddMemberDialog(QDialog):
    # This is the pop-up window for adding a new member in the members tab.
    def __init__(self, existing_members, db_seeder, librarian_id, parent=None):
        super().__init__(parent)
        self.existing_members = existing_members
        self.db_seeder = db_seeder
        self.librarian_id = librarian_id  # Store librarian_id
        self.setWindowTitle("Add New Member")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f3ed;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        # This puts together all the input boxes and buttons for the add member form
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Add New Member")
        title_label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 0px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # First Name
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setStyleSheet(self.get_input_style())
        
        # Middle Name
        self.middle_name_edit = QLineEdit()
        self.middle_name_edit.setStyleSheet(self.get_input_style())
        
        # Last Name
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setStyleSheet(self.get_input_style())
        
        # Contact Number - Use protected contact input
        self.contact_edit = ProtectedContactLineEdit()
        self.contact_edit.setStyleSheet(self.get_input_style())
        
        # Add fields to form
        form_layout.addRow(self.create_label("First Name:"), self.first_name_edit)
        form_layout.addRow(self.create_label("Middle Name:"), self.middle_name_edit)
        form_layout.addRow(self.create_label("Last Name:"), self.last_name_edit)
        form_layout.addRow(self.create_label("Contact Number:"), self.contact_edit)


        layout.addLayout(form_layout)
        layout.addSpacing(50)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Add Member button
        add_btn = QPushButton("Add Member")
        add_btn.setFixedSize(120, 40)
        add_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background-color: #5C4033;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        add_btn.clicked.connect(self.add_member)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedSize(100, 40)
        cancel_btn.setStyleSheet("""
            QPushButton {
                color: #5C4033;
                font-size: 14px;
                font-weight: bold;
                background-color: #F5F5F5;
                border: 2px solid #5C4033;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)

    def create_label(self, text):
        # Just a helper to make the labels look a bit nicer hehe
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        return label
    
    def get_input_style(self):
        # The style for the text boxes
        return """
            QLineEdit {
                color: #5C4033;
                font-size: 14px;
                padding: 8px;
                background-color: #f5f3ed;
                border: 2px solid #5C4033;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: white;
            }
        """
    def is_valid_contact(self, contact):
        # Checks if the number is really a mobile number (starts with 09 and is 11 digits)
        return contact.isdigit() and contact.startswith("09") and len(contact) == 11

    def is_valid_name(self, name):
        # Makes sure the name only has letters (and spaces)
        return name.replace(" ", "").isalpha()

    def add_member(self):
        # This runs when you click the 'Add Member' button. It checks the info and saves it if everything is okay.
        # Get the input data
        first_name = self.first_name_edit.text().strip()
        middle_name = self.middle_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        contact = self.contact_edit.text().strip()

        # VALIDATION
        if first_name and not self.is_valid_name(first_name):
            QMessageBox.warning(self, "Validation Error", "First name should contain letters only.")
            return
        
        if middle_name and not self.is_valid_name(middle_name):
            QMessageBox.warning(self, "Validation Error", "Middle name should contain letters only.")
            return
            
        if last_name and not self.is_valid_name(last_name):
            QMessageBox.warning(self, "Validation Error", "Last name should contain letters only.")
            return

        if not first_name or not last_name:
            QMessageBox.warning(self, "Validation Error", "First name and last name are required!")
            return

        if len(contact) < 11:
            QMessageBox.warning(self, "Validation Error", "Please complete the contact number!")
            return
        
        if not self.is_valid_contact(contact):
            QMessageBox.warning(self, "Validation Error", "Contact number must start with 09 and be exactly 11 digits.")
            return
        
        # Check for duplicate contact number
        if self.db_seeder.findMemberContact(contact=contact):
            QMessageBox.warning(self, "Validation Error", "This contact number is already registered!")
            return
        
        # Construct full name
        full_name = first_name
        if middle_name:
            full_name += f" {middle_name}"
        full_name += f" {last_name}"
        
        # Create member data
        self.member_data = {
            "name": full_name,
            "contact": contact
        }

        # Insert into database
        self.db_seeder.seed_data(
            tableName="Member",
            data=[
                {
                    "MemberLN": last_name,
                    "MemberFN": first_name,
                    "MemberMI": middle_name,
                    "MemberContact": contact,
                    "LibrarianID": self.librarian_id,  # Include LibrarianID
                    "isDeleted": None
                }
            ], 
            columnOrder=["MemberLN", "MemberFN", "MemberMI", "MemberContact", "LibrarianID", "isDeleted"]
        )
        
        QMessageBox.information(self, "Success", f"Member {full_name} added successfully!")
        self.accept()

class MemberEditDialog(QDialog):
    # This is the pop-up for editing or deleting a member. 
    # We can edit here po and delete
    def __init__(self, member_data, existing_members, parent=None):
        # When you open this, it loads the member's info so you can edit it
        super().__init__(parent)
        self.member_data = member_data.copy()
        self.db_seeder = DatabaseSeeder()
        self.existing_members = existing_members

        self.original_contact = str(member_data.get("MemberContact", ""))        
        self.setWindowTitle("Edit Member")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f3ed;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        # This puts together all the input boxes and buttons for editing a member
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Edit Member Information")
        title_label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
 
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        first_name = self.member_data.get("MemberFN", "")
        middle_name = self.member_data.get("MemberMI", "")
        last_name = self.member_data.get("MemberLN", "")
        
        # First Name
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setText(first_name)
        self.first_name_edit.setStyleSheet(self.get_input_style())
        
        # Middle Name
        self.middle_name_edit = QLineEdit()
        self.middle_name_edit.setText(middle_name)
        self.middle_name_edit.setStyleSheet(self.get_input_style())
        
        # Last Name
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setText(last_name)
        self.last_name_edit.setStyleSheet(self.get_input_style())
        
        self.contact_edit = ProtectedContactLineEdit()
        self.contact_edit.setText(str(self.member_data.get("MemberContact", "")))
        self.contact_edit.setStyleSheet(self.get_input_style())
            
        # Add fields to form
        form_layout.addRow(self.create_label("First Name:"), self.first_name_edit)
        form_layout.addRow(self.create_label("Middle Name:"), self.middle_name_edit)
        form_layout.addRow(self.create_label("Last Name:"), self.last_name_edit)
        form_layout.addRow(self.create_label("Contact Number:"), self.contact_edit)
        layout.addLayout(form_layout)
        layout.addSpacing(40)
        
        # Buttons
        button_layout = QHBoxLayout()

        # Save Changes button
        save_btn = QPushButton("Save Changes")
        save_btn.setFixedSize(120, 40)
        save_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background-color: #5C4033;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        
        # Delete button
        delete_btn = QPushButton("Delete")
        delete_btn.setFixedSize(100, 40)
        delete_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background-color: #D32F2F;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        delete_btn.clicked.connect(self.delete_member)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
    
    def create_label(self, text):
        # Just a helper to make the labels look a bit nicer
        label = QLabel(text)
        label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        return label
    
    def get_input_style(self):
        # This is just the style for the text boxes
        return """
            QLineEdit {
                color: #5C4033;
                font-size: 14px;
                padding: 8px;
                background-color: #f5f3ed;
                border: 2px solid #5C4033;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: white;
            }
        """
    
    def is_valid_name(self, name):
        # Makes sure the name only has letters 
        return name.replace(" ", "").isalpha()

    def is_valid_contact(self, contact):
        # Checks if the number is really a mobile number (starts with 09 and is 11 digits)
        return contact.isdigit() and contact.startswith("09") and len(contact) == 11

    def save_changes(self):
        # For Save Changes. It checks the info and updates it if everything is okay.
        first_name = self.first_name_edit.text().strip()
        middle_name = self.middle_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        contact = self.contact_edit.text().strip()
        
        if first_name and not self.is_valid_name(first_name):
            QMessageBox.warning(self, "Invalid Input", "First name should contain letters only.")
            return
        
        if middle_name and not self.is_valid_name(middle_name):
            QMessageBox.warning(self, "Invalid Input", "Middle name should contain letters only.")
            return
            
        if last_name and not self.is_valid_name(last_name):
            QMessageBox.warning(self, "Invalid Input", "Last name should contain letters only.")
            return

        if not first_name or not last_name:
            QMessageBox.warning(self, "Validation Error", "First name and last name are required!")
            return
        
        if len(contact) < 11:
            QMessageBox.warning(self, "Validation Error", "Please complete the contact number!")
            return
        
        if not self.is_valid_contact(contact):
            QMessageBox.warning(self, "Validation Error", "Contact number must start with 09 and be exactly 11 digits.")
            return
        
        if contact != self.original_contact:
            for member in self.existing_members:
                if str(member.get("MemberContact", "")) == contact:
                    QMessageBox.warning(self, "Validation Error", "This contact number is already registered!")
                    return
        
        full_name = first_name
        if middle_name:
            full_name += f" {middle_name}"
        full_name += f" {last_name}"
        
        member_id = self.member_data["MemberID"]
    
        updates = {
            "MemberFN": first_name,
            "MemberMI": middle_name,
            "MemberLN": last_name,
            "MemberContact": contact,
            "isDeleted": None
        }
        
        try:
            self.db_seeder.update_table("Member", updates, "MemberID", member_id)
            self.member_data.update(updates)
            QMessageBox.information(self, "Success", "Member information updated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update member: {str(e)}")  

    def delete_member(self):
        # For delete po. It removes the member from the database.
        first_name = self.member_data.get("MemberFN", "")
        middle_initial = self.member_data.get("MemberMI", "")
        last_name = self.member_data.get("MemberLN", "")
        full_name = f"{first_name} {middle_initial} {last_name}".strip()

        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete member {full_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_seeder.delete_table(tableName="Member", column="MemberID", value=self.member_data["MemberID"] )
                QMessageBox.information(self, "Success", f"Member {full_name} deleted successfully!")
                self.accept()  # Close the dialog after deletion
                
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete member: {str(e)}")

class MemberPreviewDialog(QDialog):
    # This is the pop-up that shows all the details about a member. You can also edit or delete them from here.
    def __init__(self, member_data, existing_members, parent=None):
        # When you open this, it loads all the member's info so you can see it
        super().__init__(parent)
        self.member_data = member_data.copy()
        self.existing_members = existing_members
        self.parent_window = parent
        self.db_seeder = DatabaseSeeder()
        
        self.setWindowTitle("Member Details")
        self.setFixedSize(450, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f3ed;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
        # This puts together all the labels and info for the member details view
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_label = QLabel("Member Details")
        title_label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Member Avatar
        first_name = self.member_data.get("MemberFN", "")
        middle_initial = self.member_data.get("MemberMI", "")
        last_name = self.member_data.get("MemberLN", "")
        full_name = f"{first_name} {middle_initial} {last_name}".strip()
        
        avatar_label = QLabel()
        avatar_pixmap = create_initials_avatar(full_name, 120)
        avatar_label.setPixmap(avatar_pixmap)
        avatar_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(avatar_label)
        
        # Member Information Container
        info_container = QWidget()
        info_container.setStyleSheet("""
            QWidget {
                background-color: #E5DBD3;
                border-radius: 15px;
                padding: 5px;
            }
        """)
        
        info_layout = QVBoxLayout(info_container)
        info_layout.setSpacing(5)
        
        # Member ID
        member_id_layout = QHBoxLayout()
        id_label = QLabel("Member ID:")
        id_label.setStyleSheet(self.get_label_style())
        id_value = QLabel(str(self.member_data.get("MemberID", "N/A")))
        id_value.setStyleSheet(self.get_value_style())
        member_id_layout.addWidget(id_label)
        member_id_layout.addStretch()
        member_id_layout.addWidget(id_value)
        info_layout.addLayout(member_id_layout)
        
        # Full Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Full Name:")
        name_label.setStyleSheet(self.get_label_style())
        name_value = QLabel(full_name)
        name_value.setStyleSheet(self.get_value_style())
        name_value.setWordWrap(True)
        name_layout.addWidget(name_label)
        name_layout.addStretch()
        name_layout.addWidget(name_value)
        info_layout.addLayout(name_layout)
        
        # First Name
        fn_layout = QHBoxLayout()
        fn_label = QLabel("First Name:")
        fn_label.setStyleSheet(self.get_label_style())
        fn_value = QLabel(first_name or "N/A")
        fn_value.setStyleSheet(self.get_value_style())
        fn_layout.addWidget(fn_label)
        fn_layout.addStretch()
        fn_layout.addWidget(fn_value)
        info_layout.addLayout(fn_layout)
        
        # Middle Name
        mn_layout = QHBoxLayout()
        mn_label = QLabel("Middle Name:")
        mn_label.setStyleSheet(self.get_label_style())
        mn_value = QLabel(middle_initial or "N/A")
        mn_value.setStyleSheet(self.get_value_style())
        mn_layout.addWidget(mn_label)
        mn_layout.addStretch()
        mn_layout.addWidget(mn_value)
        info_layout.addLayout(mn_layout)
        
        # Last Name
        ln_layout = QHBoxLayout()
        ln_label = QLabel("Last Name:")
        ln_label.setStyleSheet(self.get_label_style())
        ln_value = QLabel(last_name or "N/A")
        ln_value.setStyleSheet(self.get_value_style())
        ln_layout.addWidget(ln_label)
        ln_layout.addStretch()
        ln_layout.addWidget(ln_value)
        info_layout.addLayout(ln_layout)
        
        # Contact Number
        contact_layout = QHBoxLayout()
        contact_label = QLabel("Contact:")
        contact_label.setStyleSheet(self.get_label_style())
        contact_value = QLabel(str(self.member_data.get("MemberContact", "N/A")))
        contact_value.setStyleSheet(self.get_value_style())
        contact_layout.addWidget(contact_label)
        contact_layout.addStretch()
        contact_layout.addWidget(contact_value)
        info_layout.addLayout(contact_layout)
        
        
        layout.addWidget(info_container)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Edit Button
        edit_btn = QPushButton("✏️ Edit Member")
        edit_btn.setFixedSize(140, 45)
        edit_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background-color: #5C4033;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
        """)
        edit_btn.clicked.connect(self.edit_member)
        
        # Delete Button
        delete_btn = QPushButton("🗑️ Delete Member")
        delete_btn.setFixedSize(140, 45)
        delete_btn.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background-color: #D32F2F;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #B71C1C;
            }
        """)
        delete_btn.clicked.connect(self.delete_member)
        
        button_layout.setContentsMargins(0, 20, 0, 0)
        button_layout.addStretch()
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
    
    def get_label_style(self):
        # Just the style for the labels in the details view
        return """
            QLabel {
                color: #5C4033;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
        """
    
    def get_value_style(self):
        # Just the style for the values in the details view
        return """
            QLabel {
                color: #8B4513;
                font-size: 16px;
                font-weight: normal;
                background-color: transparent;
            }
        """
    
    def edit_member(self):
        # This opens the edit dialog for this member
        """Open the edit dialog"""
        self.close()  # Close preview dialog
        edit_dialog = MemberEditDialog(self.member_data, self.existing_members, self.parent_window)
        result = edit_dialog.exec()
        
        if result == QDialog.Accepted:
            # Refresh the parent window's member list
            if hasattr(self.parent_window, 'refresh_members_grid'):
                self.parent_window.members = self.parent_window.db_seeder.get_all_records(tableName="Member", id=self.parent_window.librarian_id)
                self.parent_window.refresh_members_grid()
    
    def delete_member(self):
        # This deletes the member and updates the list
        """Delete the member"""
        first_name = self.member_data.get("MemberFN", "")
        middle_initial = self.member_data.get("MemberMI", "")
        last_name = self.member_data.get("MemberLN", "")
        full_name = f"{first_name} {middle_initial} {last_name}".strip()

        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete member {full_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.db_seeder.delete_table(tableName="Member", column="MemberID", value=self.member_data["MemberID"])
                QMessageBox.information(self, "Success", f"Member {full_name} deleted successfully!")
                
                # Refresh the parent window's member list
                if hasattr(self.parent_window, 'refresh_members_grid'):
                    self.parent_window.members = self.parent_window.db_seeder.get_all_records(tableName="Member", id=self.parent_window.librarian_id)
                    self.parent_window.refresh_members_grid()
                
                self.accept()  # Close the preview dialog
                
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete member: {str(e)}")

class MembersMainWindow(QWidget):
    # This is the MAIN WINDOW po where we can see and manage all the members. 
    # It's the big screen for members.
    def __init__(self, librarian_id=1):  # Default librarian_id for testing
        # It loads all the members and sets up the window
        super().__init__()
        self.librarian_id = librarian_id  # Store librarian_id
        self.setWindowTitle("Library Management System - Members")
        self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()

        self.setStyleSheet("""
            MembersMainWindow {
                background-color: #f1efe3;
            }
        """)

        # Initialize members data
        self.db_seeder = DatabaseSeeder()
        self.members = self.db_seeder.get_all_records(tableName="Member", id= self.librarian_id)
        self.original_members = self.members.copy()  # Keep original data for search functionality
        
        # DEBUG: Check what we got
        print("Fetched members:", self.members)
        print("Type of members:", type(self.members))
        print("Number of members:", len(self.members) if self.members else 0)
        if self.members:
            print("First member:", self.members[0])
            print("Type of first member:", type(self.members[0]))

        self.init_ui()
    
    def init_ui(self):
        # This puts together the main layout, sidebar, and the area where members show up
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create navigation sidebar
        self.navbar = NavigationSidebar()
        self.navbar.on_navigation_clicked = nav_manager.handle_navigation
        
        # Main content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f5f3ed;")
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create members view
        self.members_view = self.create_members_view()
        self.content_layout.addWidget(self.members_view)
        
        # Add sidebar and content to main layout
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.content_area)
    
    def create_members_view(self):
        # This builds the view with the big title, search bar, and the grid of members
        """Create the main members view with title and search bar/buttons"""
        view_widget = QWidget()
        view_layout = QVBoxLayout(view_widget)
        view_layout.setContentsMargins(40, 80, 40, 20)
       
        # Header section
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("Members Management")
        title_label.setStyleSheet("""
            QLabel {
                color: #5C4033;
                font-size: 50px;
                font-weight: bold;
                background-color: transparent;
            }
        """)
        
        # Search section
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0) 
        search_layout.setSpacing(10)
        
        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search members...")
        self.search_bar.setFixedSize(300, 50)
        self.search_bar.textChanged.connect(lambda text: self.searchMembers(text))  # Search as user types
        self.search_bar.returnPressed.connect(lambda: self.searchMembers(self.search_bar.text()))  # Search on Enter
        self.search_bar.setStyleSheet("""
            QLineEdit {
                color: #5C4033;
                font-size: 16px;
                padding: 10px 15px;
                background-color: #f5f3ed;
                border: 3px solid #5C4033;
                border-radius: 10px;
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: white;
            }
        """)
        
        # Search button
        search_btn = QPushButton("🔍")
        search_btn.setFixedSize(50, 50)
        search_btn.setStyleSheet("""
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
        search_btn.clicked.connect(lambda: self.searchMembers(self.search_bar.text()))
        
        # Clear search button
        clear_btn = QPushButton("✕")
        clear_btn.setFixedSize(50, 50)
        clear_btn.setToolTip("Clear Search")
        clear_btn.setStyleSheet("""
            QPushButton {
                color: #CC4125;
                font-size: 20px;
                font-weight: bold;
                background-color: #F5F5F5;
                border: 3px solid #CC4125;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #CC4125;
                color: white;
            }
        """)
        clear_btn.clicked.connect(self.clear_search)
        
        # Add member button
        add_btn = QPushButton("➕")
        add_btn.setFixedSize(50, 50)
        add_btn.setStyleSheet("""
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
        add_btn.clicked.connect(self.add_new_member)
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(clear_btn)
        search_layout.addWidget(add_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(search_container, alignment=Qt.AlignTop)
        
        view_layout.addLayout(header_layout, stretch=0)
        view_layout.addSpacing(20)

        # Create scroll area for members
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent; 
                border: none;
            }
            QScrollBar:vertical {
                width: 0px;
            }
            QScrollBar:horizontal {
                height: 0px;
            }
        """)
        self.refresh_members_grid()

        view_layout.addWidget(self.scroll_area)

        return view_widget
    
    def add_new_member(self):
        # This opens the add member dialog if add button is clicked
        """Open the add member dialog"""
        dialog = AddMemberDialog(self.members, self.db_seeder, self.librarian_id, self)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            self.members = self.db_seeder.get_all_records(tableName="Member", id= self.librarian_id)
            self.original_members = self.members.copy()  # Update original data
            self.refresh_members_grid()

    def clear_search(self):
        # This clears the search bar and shows all the members again
        """Clear the search and restore all members"""
        self.search_bar.clear()
        self.members = self.original_members.copy()
        self.refresh_members_grid()

    def searchMembers(self, search_text):
        # This searches for members by name or contact number
        """Search members based on the input text"""
        search_text = search_text.strip()
        if not search_text:
            self.clear_search()
            return
        
        print(f"🔍 Searching members for: '{search_text}'")
        try:
            # Use database search instead of local search
            search_results = self.db_seeder.search_records("Member", search_text, self.librarian_id)
            self.members = search_results
            print(f"✅ Found {len(search_results)} matching members from database")
            
        except Exception as e:
            print(f"❌ Error searching members: {e}")
            # Fallback to local search if database search fails
            self.perform_local_member_search(search_text)
        
        self.refresh_members_grid()

    def perform_local_member_search(self, search_text):
        # If the database search doesn't work, this does a simple search in the list
        """Fallback local member search method"""
        search_text = search_text.lower()
        filtered_members = []
        for member in self.original_members:  # Search from original data
            full_name = f"{member.get('MemberFN', '')} {member.get('MemberMI', '')} {member.get('MemberLN', '')}".strip().lower()
            contact = str(member.get('MemberContact', '')).lower()
            if search_text in full_name or search_text in contact:
                filtered_members.append(member)
        
        self.members = filtered_members
        print(f"📝 Local search found {len(filtered_members)} matching members") 

    def get_active_members(self):
        # This gets only the members that aren't deleted (still active)
        """Get only active member accounts"""
        if not self.members:
            return []
        active_members = []
        for member in self.members:
            if member.get("isDeleted") is None or member.get("isDeleted") == "" and member.get("LibrarianID") == self.librarian_id:
                active_members.append(member)
        return active_members
    
    def refresh_members_grid(self):
        # This updates the grid to show the current members
        """Refresh the members grid display"""
        scroll_widget = QWidget()

        grid_layout = QGridLayout(scroll_widget)
        grid_layout.setVerticalSpacing(30)
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setContentsMargins(80, 60, 29, 30)
        grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        active_members = self.get_active_members()

        for i, member in enumerate(active_members):
            container = self.create_member_container(member, i) 
            row = i // 4
            col = i % 4
            grid_layout.addWidget(container, row, col)

        self.scroll_area.setWidget(scroll_widget)
    
    def create_member_container(self, member, index):
        # This makes a clickable card for each member, with their avatar and info
        """Create a clickable member container"""
        container = QWidget()
        container.setFixedSize(280, 240)
        container.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 28px;
                border: 3px solid #964B00;
            }
            QWidget:hover {
                border: 3px solid #5C4033;  
            }
        """)
        
        container.mousePressEvent = lambda event, m=member, idx=index: self.on_member_click(m, idx)

        # Create image label
        image_label = QLabel()
        image_label.setStyleSheet("background: transparent; border: none;")
        
        # Get member name
        first_name = member.get("MemberFN", "")
        middle_initial = member.get("MemberMI", "")
        last_name = member.get("MemberLN", "")
        full_name = f"{first_name} {middle_initial} {last_name}".strip()
        
        # Create initials avatar instead of using default image
        avatar_pixmap = create_initials_avatar(full_name, 80)
        image_label.setPixmap(avatar_pixmap)
        
        def truncate_to_two_lines(text, max_width=220, font_size=16):
            font = QFont("Times New Roman", font_size)
            font.setBold(True)
            metrics = QFontMetrics(font)
            
            single_line_width = max_width + 20
            
            if metrics.horizontalAdvance(text) <= single_line_width:
                return text
            
            words = text.split()
            line1 = ""
            line2 = ""
            
            for word in words:
                test_line = f"{line1} {word}".strip()
                if metrics.horizontalAdvance(test_line) <= single_line_width:
                    line1 = test_line
                else:
                    remaining_words = words[len(line1.split()):]
                    line2 = " ".join(remaining_words)
                    break
            
            if line2 and metrics.horizontalAdvance(line2) > single_line_width:
                while line2 and metrics.horizontalAdvance(line2 + "...") > single_line_width:
                    words_in_line2 = line2.split()
                    if len(words_in_line2) > 1:
                        words_in_line2.pop()
                        line2 = " ".join(words_in_line2)
                    else:
                        while line2 and metrics.horizontalAdvance(line2 + "...") > single_line_width:
                            line2 = line2[:-1]
                        break
                line2 += "..."
            
            if line2:
                return f"{line1}\n{line2}"
            else:
                return line1
        
        display_name = truncate_to_two_lines(full_name)
        
        memberid_label = QLabel(f'<span style="color:#5C4033;">Member ID:</span> <span style="color:#8b4513;">{member.get("MemberID", "N/A")}</span>')
        memberid_label.setStyleSheet("""
            font-size: 16px;
            font: bold;
            color: #5C4033;
            border: none;
            outline: none;
        """)
        memberid_label.setAlignment(Qt.AlignLeft)

        name_label = QLabel(f'<span style="color:#5C4033;">Name:</span> <span style="color:#8b4513;">{display_name}</span>')
        name_label.setStyleSheet("""
            font-size: 16px;
            font: bold;
            color: #5C4033;
            border: none;
            outline: none;
        """)
        name_label.setAlignment(Qt.AlignLeft)
        name_label.setWordWrap(True)
        name_label.setMaximumWidth(220)
        name_label.setFixedHeight(40)

        contact_label = QLabel(f'<span style="color:#5C4033;">Contact Number:</span> <span style="color:#8b4513;">{member.get("MemberContact", "N/A")}</span>')
        contact_label.setStyleSheet("""
            font-size: 16px;
            font: bold;
            color: #5C4033;
            border: none;
            outline: none;
        """)
        contact_label.setAlignment(Qt.AlignLeft)
        
        inner_layout = QVBoxLayout(container)
        inner_layout.addSpacing(10)
        inner_layout.addWidget(image_label, alignment=Qt.AlignCenter)
        inner_layout.setContentsMargins(30, 10, 10, 10)
        inner_layout.addSpacing(15)
        inner_layout.addWidget(memberid_label)
        inner_layout.addWidget(name_label)
        inner_layout.addWidget(contact_label)
        inner_layout.addSpacing(10)
        
        return container
    
    def on_member_click(self, member, index):
        # When you click a member, this shows their details in a pop-up
        """Handle member container click - now opens preview dialog"""
        preview_dialog = MemberPreviewDialog(member, self.members, self)
        preview_dialog.exec()

def create_initials_avatar(name, size=80):
    # Split the name into words (like first, middle, last)
    words = name.split()
    initials = ""

    # If the name has at least two words, use the first letter of the first and last word
    if len(words) >= 2:
        initials = words[0][0].upper() + words[-1][0].upper()
    # If there's only one word, just use its first letter
    elif len(words) == 1 and words[0]:
        initials = words[0][0].upper()
    # If the name is empty, show a question mark
    else:
        initials = "?"

    # Make a blank square image for the avatar
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    # Some aesthetic brown colors to pick from for the background
    primary_colors = [
        "#5C4033",  # Dark brown
        "#8B4513",  # Saddle brown
        "#A67B5B",  # Medium brown
        "#B7966B",  # Light brown
        "#964B00",  # Brown
        "#6B4423",  # Dark wood brown
        "#825D30"   # Medium wood brown
    ]

    # Pick a color based on the name, so each person gets a consistent color
    import hashlib
    hash_value = int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16)
    color_index = hash_value % len(primary_colors)
    bg_color = QColor(primary_colors[color_index])

    # Start drawing on the avatar image
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw a filled circle for the background
    painter.setBrush(QBrush(bg_color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)

    # Set up the font for the initials 
    font = QFont("Times New Roman")
    font.setPixelSize(int(size * 0.4)) 
    font.setBold(True)
    painter.setFont(font)

    # Use a light color for the text 
    painter.setPen(QColor("#FFFEF0"))  

    # Draw the initials right in the center of the circle
    painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)
    painter.end()

    # Give back the finished avatar image
    return pixmap

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Times New Roman", 10))
    from Authentication import Authentication
    window = Authentication()
    nav_manager.initialize(app)
    nav_manager._current_window = window
    window.show()
    sys.exit(app.exec())