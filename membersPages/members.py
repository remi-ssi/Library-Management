import sys
import sqlite3
from datetime import datetime
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

def get_rounded_pixmap(pixmap, size):
    rounded = QPixmap(size, size)
    rounded.fill(Qt.transparent)

    painter = QPainter(rounded)
    painter.setRenderHint(QPainter.Antialiasing)
    path = QPainterPath()
    path.addEllipse(0, 0, size, size)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, size, size, pixmap)
    painter.end()
    return rounded

class ProtectedContactLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("09")
        self.setCursorPosition(2)
        self.textChanged.connect(self.on_text_changed)
    
    def keyPressEvent(self, event):
        cursor_pos = self.cursorPosition()
        
        if event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
            if cursor_pos <= 2:
                return
        
        super().keyPressEvent(event)
    
    def on_text_changed(self, text):
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
    def __init__(self, existing_members, db_seeder, librarian_id, parent=None):
        super().__init__(parent)
        self.existing_members = existing_members
        self.db_seeder = db_seeder
        self.librarian_id = librarian_id  # Store librarian_id
        self.setWindowTitle("Add New Member")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
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
        return """
            QLineEdit {
                color: #5C4033;
                font-size: 14px;
                padding: 8px;
                background-color: #FFFEF0;
                border: 2px solid #5C4033;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: white;
            }
        """
    def is_valid_contact(self, contact):
        return contact.isdigit() and contact.startswith("09") and len(contact) == 11

    def is_valid_name(self, name):
        return name.replace(" ", "").isalpha()

    def add_member(self):
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
    def __init__(self, member_data, existing_members, parent=None):
        super().__init__(parent)
        self.member_data = member_data.copy()
        self.db_seeder = DatabaseSeeder()
        self.existing_members = existing_members

        self.original_contact = str(member_data.get("MemberContact", ""))        
        self.setWindowTitle("Edit Member")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #f1efe3;
            }
        """)
        
        self.init_ui()
    
    def init_ui(self):
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
        return """
            QLineEdit {
                color: #5C4033;
                font-size: 14px;
                padding: 8px;
                background-color: #FFFEF0;
                border: 2px solid #5C4033;
                border-radius: 6px;
            }
            QLineEdit:focus {
                border-color: #8B4513;
                background-color: white;
            }
        """
    
    def is_valid_name(self, name):
        return name.replace(" ", "").isalpha()

    def is_valid_contact(self, contact):
        return contact.isdigit() and contact.startswith("09") and len(contact) == 11

    def save_changes(self):
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

class MembersMainWindow(QWidget):
    def __init__(self, librarian_id=1):  # Default librarian_id for testing
        super().__init__()
        self.librarian_id = librarian_id  # Store librarian_id
        self.setWindowTitle("Library Management System - Members")
        self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()

        # Initialize members data
        self.db_seeder = DatabaseSeeder()
        self.members = self.db_seeder.get_all_records(tableName="Member", id= self.librarian_id)
        
        # DEBUG: Check what we got
        print("Fetched members:", self.members)
        print("Type of members:", type(self.members))
        print("Number of members:", len(self.members) if self.members else 0)
        if self.members:
            print("First member:", self.members[0])
            print("Type of first member:", type(self.members[0]))

        self.init_ui()
    
    def init_ui(self):
        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create navigation sidebar
        self.navbar = NavigationSidebar()
        self.navbar.on_navigation_clicked = nav_manager.handle_navigation
        
        # Main content area
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: #f1efe3;")
        
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create members view
        self.members_view = self.create_members_view()
        self.content_layout.addWidget(self.members_view)
        
        # Add sidebar and content to main layout
        main_layout.addWidget(self.navbar)
        main_layout.addWidget(self.content_area)
    
    def create_members_view(self):
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
        """Open the add member dialog"""
        dialog = AddMemberDialog(self.members, self.db_seeder, self.librarian_id, self)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            self.members = self.db_seeder.get_all_records(tableName="Member", id= self.librarian_id)
            self.refresh_members_grid()
        
    def get_active_members(self):
        """Get only active member accounts"""
        if not self.members:
            return []
        active_members = []
        for member in self.members:
            if member.get("isDeleted") is None or member.get("isDeleted") == "" and member.get("LibrarianID") == self.librarian_id:
                active_members.append(member)
        return active_members
    
    def refresh_members_grid(self):
        """Refresh the members grid display"""
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)
        grid_layout.setVerticalSpacing(30)
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setContentsMargins(20, 60, 29, 30)
        grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        active_members = self.get_active_members()

        for i, member in enumerate(active_members):
            container = self.create_member_container(member, i) 
            row = i // 4
            col = i % 4
            grid_layout.addWidget(container, row, col)

        self.scroll_area.setWidget(scroll_widget)
    
    def create_member_container(self, member, index):
        """Create a clickable member container"""
        container = QWidget()
        container.setFixedSize(280, 240)
        container.setStyleSheet("""
            QWidget {
                background-color: #FFFEEF;
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
        """Handle member container click"""
        dialog = MemberEditDialog(member, self.members, self)
        result = dialog.exec()

        if result == QDialog.Accepted or result == 2:  # Accepted or Delete
            try:
                self.members = self.db_seeder.get_all_records(tableName="Member", id= self.librarian_id)
                self.refresh_members_grid()
                if result == 2:
                    QMessageBox.information(self, "Success", "Member deleted successfully")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to refresh members: {str(e)}")

def create_initials_avatar(name, size=80):
    # Get initials from name
    words = name.split()
    initials = ""
    
    if len(words) >= 2:
        # Get first letter of first name and first letter of last name
        initials = words[0][0].upper() + words[-1][0].upper()
    elif len(words) == 1 and words[0]:
        # If only one name, take first letter
        initials = words[0][0].upper()
    else:
        # If no name, use question mark
        initials = "?"
    
    # Create colored background with initials
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    
    # Define theme colors - brown shades
    primary_colors = [
        "#5C4033",  # Dark brown
        "#8B4513",  # Saddle brown
        "#A67B5B",  # Medium brown
        "#B7966B",  # Light brown
        "#964B00",  # Brown
        "#6B4423",  # Dark wood brown
        "#825D30"   # Medium wood brown
    ]
    
    # Choose color based on the name (to get consistent colors for same names)
    import hashlib
    hash_value = int(hashlib.md5(name.encode('utf-8')).hexdigest(), 16)
    color_index = hash_value % len(primary_colors)
    bg_color = QColor(primary_colors[color_index])
    
    # Create painter and draw circle with text
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    
    # Draw background circle
    painter.setBrush(QBrush(bg_color))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(0, 0, size, size)
    
    # Draw text
    font = QFont("Times New Roman")
    font.setPixelSize(int(size * 0.4))  # Font size proportional to avatar size
    font.setBold(True)
    painter.setFont(font)
    
    # White text for contrast
    painter.setPen(QColor("#FFFEF0"))  
    
    # Center the text
    painter.drawText(pixmap.rect(), Qt.AlignCenter, initials)
    painter.end()
    
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