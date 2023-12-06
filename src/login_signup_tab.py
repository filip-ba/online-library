from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, 
    QFormLayout, QVBoxLayout, QTabWidget, QWidget, QMessageBox, QSpacerItem, QSizePolicy )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import Qt, QRegularExpression
import bcrypt  
from database_manager import DatabaseManager
from global_state import GlobalState
from shared_functions import create_account


class LoginSignupTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()  
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_login_signup_ui()   
		# Connects
        self.signup_button.clicked.connect(self.register_user)
        self.login_button.clicked.connect(lambda: self.login(self.username_login.text(), self.password_login.text()))
        self.logout_button.clicked.connect(self.logout) 

    def create_login_signup_ui(self):
        self.setObjectName("tab_login_signup")
        login_signup_layout = QVBoxLayout(self)
        # Add login/signup UI elements to the layout
        login_signup_tabs = QTabWidget()
        login_tab = QWidget()
        signup_tab = QWidget()
        # Layout for login_tab
        login_layout = QFormLayout(login_tab)
        login_title_label = QLabel("Log In", self)
        login_title_label.setStyleSheet("font-size: 12pt; margin-bottom: 15px;")
        login_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(login_title_label)
        self.username_login = QLineEdit()
        self.password_login = QLineEdit()
        self.password_login.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Login")
        self.logout_button = QPushButton("Logout")  # Added logout button
        login_layout.addRow("Username:", self.username_login)
        login_layout.addRow("Password:", self.password_login)
        login_layout.addRow("", self.login_button)
        login_layout.addRow("", self.logout_button)  # Added logout button
        # Layout for signup_tab
        signup_layout = QFormLayout(signup_tab)
        signup_title_label = QLabel("Sign Up", self)
        signup_title_label.setStyleSheet("font-size: 12pt; margin-bottom: 15px;")
        signup_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup_layout.addWidget(signup_title_label)
        self.username_signup = QLineEdit()
        self.username_signup.setMaxLength(40)
        self.username_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9,.-_]+")))
        self.password_signup = QLineEdit()
        self.password_signup.setMaxLength(40)
        self.password_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[^\\s]+")))
        self.password_signup.setEchoMode(QLineEdit.EchoMode.Password)
        self.first_name_signup = QLineEdit()
        self.first_name_signup.setMaxLength(40)
        self.first_name_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z]+")))
        self.last_name_signup = QLineEdit()
        self.last_name_signup.setMaxLength(40)
        self.last_name_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z]+")))
        self.ssn_signup = QLineEdit()
        self.ssn_signup.setMaxLength(10) 
        self.ssn_signup.setValidator(QIntValidator())  
        self.address_signup = QLineEdit()
        self.address_signup.setMaxLength(60)
        self.address_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9 ,.-]+")))
        self.signup_button = QPushButton("Sign Up")
        signup_layout.addRow("Username:", self.username_signup)
        signup_layout.addRow("Password:", self.password_signup)
        signup_layout.addRow("First Name:", self.first_name_signup)
        signup_layout.addRow("Last Name:", self.last_name_signup)
        signup_layout.addRow("SSN:", self.ssn_signup)
        signup_layout.addRow("Address:", self.address_signup)
        signup_layout.addRow("", self.signup_button)
        signup_layout.setContentsMargins(15, 15, 15, 15)
        login_layout.setContentsMargins(15, 15, 15, 15)
        signup_layout.setSpacing(10)
        login_layout.setSpacing(10)
        login_signup_tabs.addTab(login_tab, "Login")
        login_signup_tabs.addTab(signup_tab, "Sign Up")
        login_signup_layout.addWidget(login_signup_tabs)

    def login(self, username, password):
        if GlobalState.current_user:
            QMessageBox.information(self, "Warning", "Another user is already logged in. Please sign out first.")
            return
        user_collection = self.database_manager.db["users"]
        user_data = user_collection.find_one({"username": username})
        if user_data:
            user_role = user_data["role"]
        else:
            QMessageBox.information(self, "Login Failed", "Invalid username or password")
            return
        if bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
            GlobalState.current_user = username
            GlobalState.current_role = user_role
            self.signals.update_status.emit(f"Logged in as {GlobalState.current_user} with role {GlobalState.current_role}")
            self.username_login.setText("")
            self.password_login.setText("")
            self.update_tab_access()

    def update_tab_access(self):
        if GlobalState.current_role == "Customer":
            self.signals.update_tab_widget.emit(2)      # Sets the current tab to the customer_tab
            self.signals.customer_tab_state.emit(True, False)   # Enables the widgets
            self.signals.customer_logged_in.emit()      # Initiates the logged in customer(Loads all the tables and personal info)
        elif GlobalState.current_role == "Librarian":
            self.signals.update_tab_widget.emit(1)      
            self.signals.librarian_tab_state.emit(True, False) 
            self.signals.librarian_logged_in.emit()

    def logout(self):
        GlobalState.current_user = None
        GlobalState.current_role = None
        self.signals.customer_tab_state.emit(False, False)     # Disabling widgets in the customer_tab
        self.signals.librarian_tab_state.emit(False, False)    # Disabling widgets in the librarian_tab
        self.signals.update_status.emit("Not logged in")
        self.signals.update_status_bar_widget.emit("")  # Clear the status bar's widget after logging out
        self.statusBar.clearMessage()

    def register_user(self):
        create_account(self, self.username_signup.text(), self.password_signup.text(), "Customer", self.first_name_signup.text(), self.last_name_signup.text(), self.ssn_signup.text(), self.address_signup.text(), self.statusBar)
