import sys
from PySide6.QtCore import Qt, QSize, QPropertyAnimation
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem
)

class CollapsibleSidebar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Library Management System")
        self.setFixedSize(1300, 700)

        # Main layout
        main_layout = QHBoxLayout(self)

        # Sidebar
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setFixedWidth(60)
        self.sidebar_widget.setStyleSheet("background-color: #F0F0F0;")

        # Sidebar full layout
        full_sidebar_layout = QVBoxLayout(self.sidebar_widget)
        full_sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Toggle button at the top
        self.toggle_button = QPushButton("⇄")
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        self.toggle_button.setFixedHeight(40)
        full_sidebar_layout.addWidget(self.toggle_button, alignment=Qt.AlignTop)

        # Spacer above icons (top empty space)
        full_sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Navigation buttons layout (centered)
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setAlignment(Qt.AlignCenter)

        self.buttons = []

        #DITO YUNG ICONS
        nav_items = [
            ("dashboard.png", "Dashboard"),
            ("books.png", "Books"),
            ("members.png", "Members"),
            ("settings.png", "Settings")
        ]

        for icon_path, label in nav_items:
            btn = QPushButton()
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(24, 24))
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            btn.setMinimumHeight(40)
            btn.label_text = label
            btn.setText("")
            btn.setStyleSheet("text-align: left; padding-left: 10px;")
            self.sidebar_layout.addWidget(btn)
            self.buttons.append(btn)

        full_sidebar_layout.addLayout(self.sidebar_layout)

        # Spacer below icons (bottom empty space)
        full_sidebar_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Main content area
        self.content_area = QLabel("Main Content Area")
        self.content_area.setAlignment(Qt.AlignCenter)

        # Combine sidebar and content area
        main_layout.addWidget(self.sidebar_widget)
        main_layout.addWidget(self.content_area)

        # Animation setup
        self.expanded = False
        self.animation = QPropertyAnimation(self.sidebar_widget, b"minimumWidth")
        self.animation.setDuration(250)

    def toggle_sidebar(self):
        self.expanded = not self.expanded
        if self.expanded:
            self.animation.setStartValue(self.sidebar_widget.width())
            self.animation.setEndValue(180)
            for btn in self.buttons:
                btn.setText(f"  {btn.label_text}")
        else:
            self.animation.setStartValue(self.sidebar_widget.width())
            self.animation.setEndValue(60)
            for btn in self.buttons:
                btn.setText("")
        self.animation.start()

# Run app
app = QApplication(sys.argv)
app.setFont(QFont("Times New Roman", 10))
window = CollapsibleSidebar()
window.show()
app.exec()
