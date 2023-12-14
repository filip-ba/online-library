from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, 
    QFormLayout, QVBoxLayout, QTabWidget, QWidget, QMessageBox )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import Qt, QRegularExpression, QTimer
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
        # QTimer
        self.account_state_timer = QTimer(self)
        self.account_state_timer.timeout.connect(self.check_account_state)

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
        self.logout_button = QPushButton("Logout")  
        login_layout.addRow("Username:", self.username_login)
        login_layout.addRow("Password:", self.password_login)
        login_layout.addRow("", self.login_button)
        login_layout.addRow("", self.logout_button)  
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
        self.first_name_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[^0-9]+")))
        self.last_name_signup = QLineEdit()
        self.last_name_signup.setMaxLength(40)
        self.last_name_signup.setValidator(QRegularExpressionValidator(QRegularExpression("[^0-9]+")))
        self.ssn_signup = QLineEdit()
        self.ssn_signup.setMaxLength(10) 
        self.ssn_signup.setValidator(QIntValidator())  
        self.address_signup = QLineEdit()
        self.address_signup.setMaxLength(60)
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
        current_role = ""
        # Check if anyone is already logged in 
        if GlobalState.current_user:
            QMessageBox.information(self, "Warning", "Another user is already logged in. Please sign out first.")
            return
        # Check what role is the user logged in as(Customer/Librarian) based on the collection
        librarian_collection = self.database_manager.db["librarians"]
        librarian_data = librarian_collection.find_one({"username": username})
        if librarian_data:
            current_user = librarian_data["_id"]
            current_role = "Librarian"
            login_data = librarian_data
        # If the username is not found in the "librarians" collection, check the "users" collection
        else:
            user_collection = self.database_manager.db["users"]
            user_data = user_collection.find_one({"username": username})
            if user_data:
                current_user = user_data["_id"]
                current_role = "Customer"
                login_data = user_data
            else:
                QMessageBox.information(self, "Login Failed", "Invalid username or password")
                return
        if bcrypt.checkpw(password.encode('utf-8'), login_data["password"].encode('utf-8')):
            GlobalState.current_user = current_user
            GlobalState.current_role = current_role
            self.signals.update_status.emit(f"Logged in as {username} with role {GlobalState.current_role}")
            self.username_login.setText("") # Clear the username login form
            self.password_login.setText("") # Clear the password login form
            self.update_tab_access()    # Call a function that updates "permisisons"
        else:
            QMessageBox.information(self, "Login Failed", "Invalid username or password")
            return

    def update_tab_access(self):
        if GlobalState.current_role == "Customer":
            self.signals.customer_logged_in.emit()  # Initiate the logged in customer(Loads all the tables and personal info)
            self.signals.tab_state.emit(1, 2, 2)    # Disable tab #1, enable tab #2, move to the tab #2
            self.account_state_timer.start(60000)   # Start a timer that checks every 60s if the user wasn't banned/deleted
        elif GlobalState.current_role == "Librarian":     
            self.signals.librarian_logged_in.emit() # Initiate the logged in librarian
            self.signals.tab_state.emit(2, 1, 1)    # Disable tab #2, enable tab #1, move to the tab #1

    def check_account_state(self):
        user_id = GlobalState.current_user
        users_collection = self.database_manager.db["users"]
        banned_accounts_collection = self.database_manager.db["banned_accounts"]
        # Check if the user is in the users collection
        user_exists = users_collection.find_one({"_id": user_id})
        if not user_exists:
            # Check if the user is in the banned_accounts collection
            banned_user_exists = banned_accounts_collection.find_one({"_id": user_id})
            if banned_user_exists:
                QMessageBox.warning(self, "Account Banned", "Your account has been banned.")
            else:
                QMessageBox.warning(self, "Account Deleted", "Your account has been deleted.")
            # Log out a user if they are not found in the "users" collection
            self.logout()

    def logout(self):	
        self.account_state_timer.stop() # Stop the timer
        GlobalState.current_user = None
        GlobalState.current_role = None
        self.signals.update_status.emit("Not logged in")
        self.signals.update_status_bar_widget.emit("")  # Clear the status bar's widgets after logging out
        self.signals.update_status_bar_widget_2.emit("")  
        self.statusBar.clearMessage()
        self.signals.tab_state.emit(1, 0, 0)    # Disable tab #1
        self.signals.tab_state.emit(2, 0, 0)    # Disable tab #2

    def register_user(self):
        account_registered = create_account(self, self.username_signup.text(), self.password_signup.text(), self.first_name_signup.text(), 
                                            self.last_name_signup.text(), self.ssn_signup.text(), self.address_signup.text(), "Customer", self.statusBar)
        # Clear the forms if the account has been successfully registered
        if account_registered == True:
            self.username_signup.setText("")
            self.password_signup.setText("")
            self.first_name_signup.setText("")
            self.last_name_signup.setText("")
            self.ssn_signup.setText("")
            self.address_signup.setText("")