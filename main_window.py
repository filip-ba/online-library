from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QTabWidget
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import pyqtSignal, QObject
import os
from database_manager import DatabaseManager
from librarian.librarian_tab import LibrarianTab
from customer.customer_tab import CustomerTab
from login_signup_tab import LoginSignupTab
from global_state import GlobalState


class MainWindow(QMainWindow):
    def __init__(self, database_manager: DatabaseManager):
        super().__init__()
        self.database_manager = database_manager
        self.signals = AppSignals()
        self.create_ui()
        # Connects
        self.signals.update_status.connect(self.update_status_label)
        self.signals.update_status_bar_widget.connect(self.update_status_bar_widget)
        self.signals.update_status_bar_widget_2.connect(self.update_status_bar_widget_2)
        self.signals.tab_state.connect(self.set_tab_state)
        self.signals.log_out.connect(self.login_signup_tab.logout)
        
    def create_ui(self):
        # Set the application icon
        script_path = os.path.abspath(__file__)
        icon_path = os.path.join(os.path.dirname(script_path), "icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Online Library Management System")
        self.setGeometry(50, 50, 1000, 800)
        # Create main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        # Status bar 
        self.statusBar = self.statusBar()
        self.status_label = QLabel("Not logged in")
        self.statusBar.addPermanentWidget(self.status_label)
        self.status_bar_widget = QLabel("")
        self.statusBar.addWidget(self.status_bar_widget)
        self.status_bar_widget_2 = QLabel("")
        self.statusBar.addWidget(self.status_bar_widget_2)
        # Tab Widget for librarian, customer, and login/signup views
        self.tab_widget = QTabWidget(self)
        self.librarian_tab = LibrarianTab(self.database_manager, self.statusBar, self.signals)
        customer_tab = CustomerTab(self.database_manager, self.statusBar, self.signals)
        self.login_signup_tab = LoginSignupTab(self.database_manager, self.statusBar, self.signals)
        self.tab_widget.addTab(self.login_signup_tab, "Login/Sign up")
        self.tab_widget.addTab(self.librarian_tab, "Librarian")
        self.tab_widget.addTab(customer_tab, "Customer")
        self.tab_widget.setTabEnabled(1, False)
        self.tab_widget.setTabEnabled(2, False)
        main_layout.addWidget(self.tab_widget)
        # MenuBar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        user_menu = menu_bar.addMenu("User Menu")
        # Export and import actions
        self.export_action = QAction("Export Collections", self)
        self.import_action = QAction("Import Collections", self)
        file_menu.addAction(self.export_action)
        file_menu.addAction(self.import_action)
        self.import_action.setDisabled(True)
        self.export_action.triggered.connect(self.export_collections)
        self.import_action.triggered.connect(self.import_collections)
        self.export_action.setDisabled(True)
        file_menu.addSeparator()
        # Quit action
        self.quit_action = QAction("Quit", self)
        file_menu.addAction(self.quit_action)  
        self.quit_action.triggered.connect(self.close)
        # Logout action
        self.logout_action = QAction("Logout", self)
        user_menu.addAction(self.logout_action) 
        self.logout_action.triggered.connect(self.login_signup_tab.logout)

    def export_collections(self):
        self.signals.export_signal.emit()

    def import_collections(self):
        self.signals.import_signal.emit()
        
    def closeEvent(self, event):
        event.accept()

    def update_status_bar_widget(self, message):
        self.status_bar_widget.setText(message)

    def update_status_bar_widget_2(self, message):
        self.status_bar_widget_2.setText(message)

    def update_status_label(self, message):
        self.status_label.setText(message)
        # Disable the export and import action if the librarian isn't logged in
        if GlobalState.current_role == "Customer" or GlobalState.current_role == None:
            self.export_action.setDisabled(True)
            self.import_action.setDisabled(True)
        else:
            self.export_action.setDisabled(False)
            self.import_action.setDisabled(False)

    def update_tab_widget(self, tab_index):
        self.tab_widget.setCurrentIndex(tab_index)  

    def set_tab_state(self, disable_tab, enable_tab, set_tab):
        self.tab_widget.setTabEnabled(disable_tab, False)
        self.tab_widget.setTabEnabled(enable_tab, True)
        self.tab_widget.setCurrentIndex(set_tab)    


class AppSignals(QObject):
    update_status = pyqtSignal(str)
    update_status_bar_widget = pyqtSignal(str)
    update_status_bar_widget_2 = pyqtSignal(str)
    customer_logged_in = pyqtSignal()
    librarian_logged_in = pyqtSignal()
    tab_state = pyqtSignal(int, int, int)
    log_out = pyqtSignal()
    export_signal = pyqtSignal()
    import_signal = pyqtSignal()