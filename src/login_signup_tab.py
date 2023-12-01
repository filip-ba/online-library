from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, 
    QRadioButton, QFormLayout, QVBoxLayout, QTabWidget, QWidget, QMessageBox )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import Qt, QRegularExpression
import bcrypt  
from database_manager import DatabaseManager
from global_state import GlobalState


class LoginSignupTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()  
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_login_signup_ui()   
		
    def create_login_signup_ui(self):
        self.setObjectName("tab_login_signup")
        login_signup_layout = QVBoxLayout(self)
        # Add login/signup UI elements to the layout
        login_signup_tabs = QTabWidget()
        login_tab = QWidget()
        signup_tab = QWidget()
        # Layout for login_tab
        login_layout = QFormLayout(login_tab)
        username_login = QLineEdit()
        password_login = QLineEdit()
        password_login.setEchoMode(QLineEdit.EchoMode.Password)
        role_customer_radio = QRadioButton("Customer")
        role_librarian_radio = QRadioButton("Librarian")
        role_customer_radio.setChecked(True)
        login_button = QPushButton("Login")
        logout_button = QPushButton("Logout")  # Added logout button
        login_layout.addRow("Username:", username_login)
        login_layout.addRow("Password:", password_login)
        login_layout.addRow("Role:", role_customer_radio)
        login_layout.addWidget(role_librarian_radio)
        login_layout.addRow("", login_button)
        login_layout.addRow("", logout_button)  # Added logout button
        # Layout for signup_tab
        signup_layout = QFormLayout(signup_tab)
        signup_title_label = QLabel("Customer Registration", self)
        signup_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup_layout.addWidget(signup_title_label)
        username_signup = QLineEdit()
        username_signup.setMaxLength(30)
        username_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9,.-_]+")))
        password_signup = QLineEdit()
        password_signup.setMaxLength(30)
        password_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[^\\s]+")))
        password_signup.setEchoMode(QLineEdit.EchoMode.Password)
        first_name_signup = QLineEdit()
        first_name_signup.setMaxLength(30)
        first_name_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z]+")))
        last_name_signup = QLineEdit()
        last_name_signup.setMaxLength(30)
        last_name_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z]+")))
        ssn_signup = QLineEdit()
        ssn_signup.setMaxLength(10) 
        ssn_signup.setValidator(QIntValidator())  
        address_signup = QLineEdit()
        address_signup.setMaxLength(50)
        address_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z0-9 ,.-]+")))
        signup_button = QPushButton("Sign Up")
        signup_layout.addRow("Username:", username_signup)
        signup_layout.addRow("Password:", password_signup)
        signup_layout.addRow("First Name:", first_name_signup)
        signup_layout.addRow("Last Name:", last_name_signup)
        signup_layout.addRow("SSN:", ssn_signup)
        signup_layout.addRow("Address:", address_signup)
        signup_layout.addRow("", signup_button)
        # Add tabs to the login/signup tab widget
        login_signup_tabs.addTab(login_tab, "Login")
        login_signup_tabs.addTab(signup_tab, "Sign Up")
        login_signup_layout.addWidget(login_signup_tabs)
        # Connects
        signup_button.clicked.connect(lambda: self.create_account(username_signup.text(), password_signup.text(), "Customer", first_name_signup.text(), last_name_signup.text(), ssn_signup.text(), address_signup.text()))
        login_button.clicked.connect(lambda: self.login(username_login.text(), password_login.text(), "Customer" if role_customer_radio.isChecked() else "Librarian"))
        logout_button.clicked.connect(self.logout) 

    def login(self, username, password, role):
        if GlobalState.current_user:
            QMessageBox.information(self, "Warning", "Another user is already logged in. Please sign out first.")
            return
        user_collection = self.database_manager.db["librarians" if role == "Librarian" else "customers"]
        user_data = user_collection.find_one({"username": username})
        if user_data and role == "Customer":
            if user_data["acc_activated"] == False:
                QMessageBox.information(self, "Inactivated account", "Your account hasen't been activated yet.")
                return
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
            GlobalState.current_user = username
            GlobalState.current_role = role
            self.signals.update_status.emit(f"Logged in as {GlobalState.current_user} with role {GlobalState.current_role}")
            self.update_tab_access()
        else:
            QMessageBox.information(self, "Login Failed", "Invalid username or password")

    def update_tab_access(self):
        if GlobalState.current_role == "Customer":
            self.signals.update_tab_widget.emit(2)      # Sets the current tab to the customer_tab
            self.signals.customer_tab_state.emit(True)  # Enables the widgets
            self.signals.customer_logged_in.emit()      # Initiates the logged in customer(Loads all the tables and personal info)
        elif GlobalState.current_role == "Librarian":
            self.signals.update_tab_widget.emit(1)      
            self.signals.librarian_tab_state.emit(True) 
            self.signals.librarian_logged_in.emit()

    def logout(self):
        GlobalState.current_user = None
        GlobalState.current_role = None
        self.signals.customer_tab_state.emit(False)     # Disabling widgets in the customer_tab
        self.signals.librarian_tab_state.emit(False)    # Disabling widgets in the librarian_tab
        self.signals.update_status.emit("Not logged in")

    def create_account(self, username, password, role, first_name, last_name, ssn, address):
        # Check if any required field is empty
        if any(not field for field in [username, password, role, first_name, last_name, ssn, address]):
            QMessageBox.information(self, "Registration Failed", "Please fill in all the required fields.")
            return
        # Check if the username or SSN already exists in the database
        customer_collection = self.database_manager.db["customers"]
        existing_username = customer_collection.find_one({"username": username})
        existing_ssn = customer_collection.find_one({"ssn": ssn})
        if existing_username and existing_ssn:
            QMessageBox.information(self, "Registration Failed", "Username and birth number already exist.")
        elif existing_username:
            QMessageBox.information(self, "Registration Failed", "Username already exists.")
        elif existing_ssn:
            QMessageBox.information(self, "Registration Failed", "Birth number already exists.")
        else:
            # Save the new customer into the customers collection
            new_customer = {
                "username": username,
                "password": str(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), 'utf-8'),  
                "role": role,
                "first_name": first_name,
                "last_name": last_name,
                "ssn": ssn,
                "address": address,
                "acc_activated": False,  
            }
            customer_collection.insert_one(new_customer)
            QMessageBox.information(self, "Customer registered", "Registration was successful. Waiting for approval.")
            # Show informational message in the status bar
            self.statusBar.showMessage(f"Registration successful. Waiting for librarian approval.", 5000)