from PyQt6.QtWidgets import ( 
    QDialog, QLabel, QLineEdit, QPushButton, QSpacerItem, 
    QHBoxLayout, QVBoxLayout, QFormLayout )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import Qt, QRegularExpression


class RegistrationDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.create_dialog_ui()
        # Connects
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def create_dialog_ui(self):
        self.setWindowTitle("Customer Registration")
        self.setFixedSize(500, 300)    
        layout = QVBoxLayout()
        window_title_label = QLabel("Register a Customer")
        window_title_label.setStyleSheet("font-size: 14pt;")
        window_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        window_title_label.setToolTip("You can register a customer.")
        layout.addWidget(window_title_label)
        # Form layout
        form_layout = QFormLayout()
        # Username
        username_signup = QLabel("Username:")
        self.username_signup = QLineEdit()
        self.username_signup.setMaxLength(40)
        self.username_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9,.-_]+")))
        form_layout.addRow(username_signup, self.username_signup)
        # Password
        password_title = QLabel("Password:")
        self.password_signup = QLineEdit()
        self.password_signup.setMaxLength(40)
        self.password_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[^\\s]+")))
        self.password_signup.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(password_title, self.password_signup)
        # First Name
        first_name_signup_title = QLabel("First Name:")
        self.first_name_signup = QLineEdit()
        self.first_name_signup.setMaxLength(40)
        self.first_name_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z]+")))
        form_layout.addRow(first_name_signup_title, self.first_name_signup)
        # Last Name
        last_name_signup_title = QLabel("Last Name:")
        self.last_name_signup = QLineEdit()
        self.last_name_signup.setMaxLength(40)
        self.last_name_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z]+")))
        form_layout.addRow(last_name_signup_title, self.last_name_signup)
        # SSN
        ssn_signup_title = QLabel("SSN:")
        self.ssn_signup = QLineEdit()
        self.ssn_signup.setMaxLength(10) 
        self.ssn_signup.setValidator(QIntValidator())  
        form_layout.addRow(ssn_signup_title, self.ssn_signup)
        # Address
        address_signup_title = QLabel("Address:")
        self.address_signup = QLineEdit()
        self.address_signup.setMaxLength(60)
        self.address_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9 ,.-]+")))
        form_layout.addRow(address_signup_title, self.address_signup)
        # Adding the form layout to the vertical layout
        form_layout.setSpacing(10)  # Adding a space between the forms
        layout.addLayout(form_layout)
        layout.addSpacerItem(QSpacerItem(10, 10))   # Adding a space after the form layout
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Register User")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        # Set the layout
        self.setLayout(layout)