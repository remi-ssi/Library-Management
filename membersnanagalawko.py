#labyu rems wala pa ko maisip na picture
import sys
import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QPainterPath
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QScrollArea, QGridLayout,
    QDialog, QFormLayout, QMessageBox
)

#4px - size of border
#10px - radius

# Import the reusable navigation sidebar
from navigation_sidebar import NavigationSidebar
from navbar_logic import nav_manager

#connect to database seeder 
from tryDatabase import DatabaseSeeder

#WALA TO WAG NIYONG PANSININ TO PARA LANG MAGING ROUND ANG PIC
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

#PARA SA CONTACT LANG THIS SO WAG DIN PANSININ
class ProtectedContactLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("09")
        self.setCursorPosition(2)  # Place cursor after "09"
        self.textChanged.connect(self.on_text_changed)
    
    def keyPressEvent(self, event):
        # Get current cursor position
        cursor_pos = self.cursorPosition()
        
        # Prevent deletion of "09" prefix
        if event.key() in [Qt.Key_Backspace, Qt.Key_Delete]:
            if cursor_pos <= 2:
                return  # Don't allow deletion of "09"
        
        # Call parent implementation
        super().keyPressEvent(event)
    
    # Ensure text always starts with "09"
    def on_text_changed(self, text):
        if not text.startswith("09"):
            self.blockSignals(True)
            # Extract only the digits after "09"
            digits_only = ''.join(filter(str.isdigit, text))
            if digits_only.startswith("09"):
                # Keep as is if already starts with 09
                clean_text = digits_only[:11]
            else:
                # Add 09 prefix to remaining digits
                remaining_digits = digits_only[2:] if digits_only.startswith("9") else digits_only
                clean_text = "09" + remaining_digits[:9]  # 09 + 9 more digits = 11 total
            
            self.setText(clean_text)
            self.setCursorPosition(len(clean_text))
            self.blockSignals(False)
        
        # Limit to 11 characters
        elif len(text) > 11:
            self.blockSignals(True)
            self.setText(text[:11])
            self.blockSignals(False)

class AddMemberDialog(QDialog):
    def __init__(self, existing_members, db_seeder, parent=None):
        super().__init__(parent)
        self.existing_members = existing_members
        self.db_seeder = DatabaseSeeder()
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

        #to insert the entry to the database
        cursor, conn = self.db_seeder.get_connection_and_cursor()
        self.db_seeder.seed_data(tableName="Member",
                                 data=[
                                     {
                                         "MemberLN" : last_name,
                                         "MemberFN" : first_name,
                                         "MemberMI": middle_name,
                                         "MemberContact": contact
                                     }
                                 ], 
                                 columnOrder=["MemberLN", "MemberFN", "MemberMI", "MemberContact"])
        
        QMessageBox.information(self, "Success", f"Member {full_name} added successfully!")
        self.accept()

class MemberEditDialog(QDialog):
    def __init__(self, member_data, existing_members, parent=None):
        super().__init__(parent)
        self.member_data = member_data.copy()
        self.db_seeder = DatabaseSeeder()  #initialize the database seeder
        self.existing_members = existing_members

        self.original_contact = str(member_data.get("MemberContact", ""))  # Use parentheses, not brackets        
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

        # Fix: Get name parts from database fields directly
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
        
        # Contact Number - Fix: Use correct database key
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
        # Fixed variable names here
        first_name = self.first_name_edit.text().strip()
        middle_name = self.middle_name_edit.text().strip()
        last_name = self.last_name_edit.text().strip()
        contact = self.contact_edit.text().strip()
        
        # Validate name fields (only check non-empty names)
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
        
        # Added contact validation
        if not self.is_valid_contact(contact):
            QMessageBox.warning(self, "Validation Error", "Contact number must start with 09 and be exactly 11 digits.")
            return
        
        # Check for duplicate contact number (only if contact was changed)
        if contact != self.original_contact:
            for member in self.existing_members:
                # Fix: Use correct database key for comparison
                if str(member.get("MemberContact", "")) == contact:
                    QMessageBox.warning(self, "Validation Error", "This contact number is already registered!")
                    return
        
        # Construct full name
        full_name = first_name
        if middle_name:
            full_name += f" {middle_name}"
        full_name += f" {last_name}"
        
        # Update member data
        member_id = self.member_data["MemberID"]  # Fix: Use correct key
    
        updates = {
            "MemberFN": first_name,
            "MemberMI": middle_name,
            "MemberLN": last_name,
            "MemberContact": contact
        }
        
        try:
            self.db_seeder.update_table("Member", updates, "MemberID", member_id)
            
            # Update the local member_data for the parent window
            self.member_data.update(updates)
            
            QMessageBox.information(self, "Success", "Member information updated successfully!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to update member: {str(e)}")
    
    def delete_member(self):
         # Build the full name from database fields
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
                # Delete from database using your existing function
                member_id = self.member_data.get("MemberID")
                self.db_seeder.delete_table("Member", "MemberID", member_id)
                
                QMessageBox.information(self, "Success", "Member deleted successfully!")
                self.done(2)  # Custom return value for delete
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete member: {str(e)}")

class MembersMainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System - Members")
        self.setGeometry(100, 100, 1200, 800)
        self.showMaximized()

        # Initialize members data
        self.db_seeder = DatabaseSeeder()
        self.members = self.db_seeder.get_all_records(tableName="Member")
        
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
        #FOR THE HEADER AND SEARCH LAYOUT -
        view_layout.setContentsMargins(40, 80, 40, 20) #left, top, right, bottom
        
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
        # Connect the add button to the add member function
        add_btn.clicked.connect(self.add_new_member)
        
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(search_btn)
        search_layout.addWidget(add_btn)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(search_container, alignment=Qt.AlignTop)
        
        view_layout.addLayout(header_layout, stretch=0)
        # Reduced spacing between header and members grid
        view_layout.addSpacing(20)

        # Create scroll area for members
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        # Hide scroll bars and make background transparent
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
        # Create and populate the members grid
        self.refresh_members_grid()

        # Add scroll area to main view layout
        view_layout.addWidget(self.scroll_area)

        return view_widget
    
    def add_new_member(self):
        """Open the add member dialog"""
        dialog = AddMemberDialog(self.members, self.db_seeder)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            self.members = self.db_seeder.get_all_records(tableName="Member")
            self.refresh_members_grid()
    
    def refresh_members_grid(self):
        """Refresh the members grid display"""
        # Container inside scroll area
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)
        # Increased vertical spacing between rows from 100 to 30
        grid_layout.setVerticalSpacing(30)
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setContentsMargins(20, 60, 29, 30)

        # Create rounded containers dynamically
        for i, member in enumerate(self.members):
            container = self.create_member_container(member, i)
            row = i // 4
            col = i % 4
            grid_layout.addWidget(container, row, col)

        self.scroll_area.setWidget(scroll_widget)
    
    def create_member_container(self, member, index):
        """Create a clickable member container"""
        container = QWidget()
        container.setFixedSize(280, 220) #width, height
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
        
        # Make container clickable
        container.mousePressEvent = lambda event, m=member, idx=index: self.on_member_click(m, idx)

        image_label = QLabel()
        image_label.setStyleSheet("background: transparent; border: none;")
        pixmap = QPixmap("assets/default_cover.jpg")  
        pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        rounded_pixmap = get_rounded_pixmap(pixmap, 80)
        image_label.setPixmap(rounded_pixmap)
        
        # Build the full name from database fields
        first_name = member.get("MemberFN", "")
        middle_initial = member.get("MemberMI", "")
        last_name = member.get("MemberLN", "")
        full_name = f"{first_name} {middle_initial} {last_name}".strip()
        
        memberid_label = QLabel(f'<span style="color:#5C4033;">Member ID:</span> <span style="color:#8b4513;">{member.get("MemberID", "N/A")}</span>')
        memberid_label.setStyleSheet("""
            font-size: 16px;
            font: bold;
            color: #5C4033;
            border: none;
            outline: none;
        """)
        memberid_label.setAlignment(Qt.AlignLeft)

        name_label = QLabel(f'<span style="color:#5C4033;">Name:</span> <span style="color:#8b4513;">{full_name}</span>')
        name_label.setStyleSheet("""
            font-size: 16px;
            font: bold;
            color: #5C4033;
            border: none;
            outline: none;
        """)
        name_label.setAlignment(Qt.AlignLeft)

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

        if result == QDialog.Accepted:
            self.members = self.db_seeder.get_all_records(tableName="Member")
            self.refresh_members_grid()

        elif result == 2:  # Delete
            try:
                # Remove the member from the local list
                self.members.pop(index)
                self.refresh_members_grid()
                QMessageBox.information(self, "Success", "Member deleted successfully")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", f"Failed to delete member: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Times New Roman", 10))
    window = MembersMainWindow()
    nav_manager._current_window = window
    window.show()
    sys.exit(app.exec())