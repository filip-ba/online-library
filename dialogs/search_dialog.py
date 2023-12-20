from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QSpacerItem, 
    QPushButton, QFormLayout, QHBoxLayout )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtCore import Qt


class SearchDialog(QDialog):
    def __init__(self, role, label_1, label_2, label_3, label_4):
        super().__init__()
        self.role = role
        # Display different labels for customer and librarian
        self.label_1 = label_1
        self.label_2 = label_2
        self.label_3 = label_3
        self.label_4 = label_4
        self.create_dialog_ui()
        # Connects
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def create_dialog_ui(self):
        self.setWindowTitle("Advanced Search")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        title_label = QLabel("Advanced Search")
        title_label.setStyleSheet("font-size: 14pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        # Form layout
        form_layout = QFormLayout()
        # Input filed 1
        label_1 = QLabel(self.label_1)
        self.input_1 = QLineEdit()
        self.input_1.setMaxLength(60)
        self.input_1.setValidator(QRegularExpressionValidator(QRegularExpression("[^0-9]+")))
        form_layout.addRow(label_1, self.input_1)
        # Input filed 2
        label_2 = QLabel(self.label_2)
        self.input_2 = QLineEdit()
        self.input_2.setMaxLength(60)
        if self.role == "Librarian":
            self.input_2.setValidator(QRegularExpressionValidator(QRegularExpression("[^0-9]+")))
        form_layout.addRow(label_2, self.input_2)
        # Input filed 3
        label_3 = QLabel(self.label_3)
        self.input_3 = QLineEdit()
        if self.role == "Librarian":
            self.input_3.setMaxLength(10)
        else:
            self.input_3.setMaxLength(4)
        self.input_3.setValidator(QIntValidator())  
        form_layout.addRow(label_3, self.input_3)
        # Input filed 4
        if self.role == "Librarian":
            label_4 = QLabel(self.label_4)
            self.input_4 = QLineEdit()
            self.input_4.setMaxLength(60)
            form_layout.addRow(label_4, self.input_4)
        # Form layout
        form_layout.setSpacing(10)
        layout.addLayout(form_layout)
        layout.addSpacerItem(QSpacerItem(10, 10))  
        # Ok and Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        # Set the layout
        self.setLayout(layout)