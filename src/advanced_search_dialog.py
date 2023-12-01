from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QPushButton, QRadioButton, QFormLayout )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import QRegularExpression


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
        # Radio buttons for choosing between sorting and searching
        self.sort_radio = QRadioButton("Sort")
        self.search_radio = QRadioButton("Search")
        self.search_radio.setChecked(True)
        radio_layout = QVBoxLayout()
        radio_layout.addWidget(self.sort_radio)
        radio_layout.addWidget(self.search_radio)
        layout.addLayout(radio_layout)
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
        self.title_input.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z ]+")))
        form_layout.addRow(self.title_label, self.title_input)
        self.year_label = QLabel("Year:")
        self.year_input = QLineEdit()
        self.year_input.setMaxLength(4)
        self.year_input.setValidator(QIntValidator())  
        form_layout.addRow(self.year_label, self.year_input)
        layout.addLayout(form_layout)
        # Buttons
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)
        self.setLayout(layout)