from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpacerItem, 
    QPushButton, QFormLayout, QHBoxLayout )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtCore import Qt


class AdvancedSearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.create_dialog_ui()
        # Connects
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def create_dialog_ui(self):
        self.setWindowTitle("Advanced Search")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        title_label = QLabel("Advanced Search")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setToolTip("Search books based on author, title, and year. Minimum length: 3 characters.")
        layout.addWidget(title_label)
        # Form layout for author, title, and year fields
        form_layout = QFormLayout()
        self.author_label = QLabel("Author:")
        self.author_input = QLineEdit()
        self.author_input.setMaxLength(40)
        self.author_input.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z ]+")))
        form_layout.addRow(self.author_label, self.author_input)
        self.title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setMaxLength(40)
        self.title_input.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9,.-_ ]+")))
        form_layout.addRow(self.title_label, self.title_input)
        self.year_label = QLabel("Year:")
        self.year_input = QLineEdit()
        self.year_input.setMaxLength(4)
        self.year_input.setValidator(QIntValidator())  
        form_layout.addRow(self.year_label, self.year_input)
        form_layout.setSpacing(10)
        layout.addLayout(form_layout)
        layout.addSpacerItem(QSpacerItem(10, 10)) 
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        # Set the layout
        self.setLayout(layout)