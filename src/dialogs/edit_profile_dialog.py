from PyQt6.QtWidgets import ( 
    QDialog, QLabel, QLineEdit, QPushButton, QSpacerItem, 
    QHBoxLayout, QVBoxLayout, QFormLayout )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import Qt, QRegularExpression


class EditProfileDialog(QDialog):
    def __init__(self, user_data, role):
        super().__init__()
        self.user_data = user_data
        self.role = role
        self.create_dialog_ui()
        # Connects
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def create_dialog_ui(self):
        self.setWindowTitle("Edit Account Details")
        self.setFixedSize(500, 300)    
        layout = QVBoxLayout()
        window_title_label = QLabel("Edit Account Details")
        window_title_label.setStyleSheet("font-size: 14pt;")
        window_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(window_title_label)
        # Form layout
        form_layout = QFormLayout()
        # Username
        username_label = QLabel("Username:")
        self.username_input = QLineEdit(self.user_data.get("username", ""))
        self.username_input.setMaxLength(40)
        self.username_input.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9,.-_]+")))
        form_layout.addRow(username_label, self.username_input)
        # Password
        if self.role == "Customer":
            password_label = QLabel("Password:")
            self.password_input = QLineEdit()
            self.password_input.setMaxLength(40)
            self.password_input.setValidator(QRegularExpressionValidator(QRegularExpression("[^\\s]+")))
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            form_layout.addRow(password_label, self.password_input)
        # First Name
        first_name_label = QLabel("First Name:")
        self.first_name_input = QLineEdit(self.user_data.get("first_name", ""))
        self.first_name_input.setMaxLength(40)
        self.first_name_input.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z]+")))
        form_layout.addRow(first_name_label, self.first_name_input)
        # Last Name
        last_name_label = QLabel("Last Name:")
        self.last_name_input = QLineEdit(self.user_data.get("last_name", ""))
        self.last_name_input.setMaxLength(40)
        self.last_name_input.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z]+")))
        form_layout.addRow(last_name_label, self.last_name_input)
        # SSN
        ssn_label = QLabel("SSN:")
        self.ssn_input = QLineEdit(self.user_data.get("ssn", ""))
        self.ssn_input.setMaxLength(10)
        self.ssn_input.setValidator(QIntValidator())  
        form_layout.addRow(ssn_label, self.ssn_input)
        # Address
        address_label = QLabel("Address:")
        self.address_input = QLineEdit(self.user_data.get("address", ""))
        self.address_input.setMaxLength(60)
        self.address_input.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9 ,.-]+")))
        form_layout.addRow(address_label, self.address_input)
        # Adding the form layout to the vertical layout
        form_layout.setSpacing(10)  # Adding a space between the forms
        layout.addLayout(form_layout)
        layout.addSpacerItem(QSpacerItem(10, 10))   # Adding a space after the form layout
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Confirm")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        # Set the layout
        self.setLayout(layout)