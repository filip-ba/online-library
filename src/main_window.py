from PyQt6.QtWidgets import  QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtCore import pyqtSignal, Qt, QObject
from database_manager import DatabaseManager
from librarian_tab import LibrarianTab
from customer_tab import CustomerTab
from login_signup_tab import LoginSignupTab


class MainWindow(QMainWindow):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        self.signals = AppSignals()
        self.setWindowTitle("Online Library Management System")
        self.setGeometry(50, 50, 700, 500)
        # Create main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        heading_label = QLabel("Library Management System", self)
        heading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(heading_label)
        # Status bar to display login status
        self.statusBar = self.statusBar()
        self.status_label = QLabel("Not logged in")
        self.statusBar.addPermanentWidget(self.status_label)
        self.status_bar_widget = QLabel("")
        self.statusBar.addWidget(self.status_bar_widget)
        # Tab Widget for librarian, customer, and login/signup views
        self.tab_widget = QTabWidget(self)
        librarian_tab = LibrarianTab(self.database_manager, self.statusBar, self.signals)
        customer_tab = CustomerTab(self.database_manager, self.statusBar, self.signals)
        login_signup_tab = LoginSignupTab(self.database_manager, self.statusBar, self.signals)
        # Add tabs to the tab widget
        self.tab_widget.addTab(login_signup_tab, "Login/Sign up")
        self.tab_widget.addTab(librarian_tab, "Librarian")
        self.tab_widget.addTab(customer_tab, "Customer")
        main_layout.addWidget(self.tab_widget)
        # Connects
        self.signals.update_status.connect(self.update_status_label)
        self.signals.update_status_bar_widget.connect(self.update_status_bar_widget)
        self.signals.update_tab_widget.connect(self.update_tab_widget)

    def update_status_bar_widget(self, message):
        self.status_bar_widget.setText(message)

    def update_status_label(self, message):
        self.status_label.setText(message)

    def update_tab_widget(self, tab_index):
        self.tab_widget.setCurrentIndex(tab_index)  


class AppSignals(QObject):
    update_status = pyqtSignal(str)
    update_status_bar_widget = pyqtSignal(str)
    update_tab_widget = pyqtSignal(int)
    customer_tab_state = pyqtSignal(bool)
    customer_logged_in = pyqtSignal()
    librarian_tab_state = pyqtSignal(bool)
    librarian_logged_in = pyqtSignal()


