from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QComboBox, QListView, QSpacerItem, QSizePolicy,  
      QInputDialog, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QDialog, QGroupBox, QHeaderView )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from database_manager import DatabaseManager
from shared_functions import create_account
from dialogs.registration_dialog import RegistrationDialog


class ManageCustomersTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_tab_ui()
        # Singals
        self.signals.librarian_tab_state.connect(self.set_tab_state)
        self.signals.librarian_logged_in.connect(self.init_librarian_tab)
        # Connects
        self.refresh_button.clicked.connect(self.display_customers)
        self.add_account_button.clicked.connect(self.register_user)

    def init_librarian_tab(self):
        self.display_customers()

    def set_tab_state(self, state, state_2):
        pass

    def create_tab_ui(self):
        # Layouts
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
        # Import/Export Layout
        group_box_2 = QGroupBox("Import/Export")
        import_export_layout = QHBoxLayout(group_box_2)
        import_button = QPushButton("Import")
        export_button = QPushButton("Export")
        import_export_layout.addWidget(import_button)
        import_export_layout.addWidget(export_button)
        # Search and Sort Layout
        group_box_1 = QGroupBox("Search/Sort Actions")
        search_sort_layout = QVBoxLayout(group_box_1)
        self.search_button = QPushButton("Open Search")
        self.sort_button = QPushButton("Open Sort Options")
        self.cancel_button = QPushButton("Cancel Selected Filters")
        self.refresh_button = QPushButton("Refresh List")
        search_sort_layout.addWidget(self.search_button)
        search_sort_layout.addWidget(self.sort_button)
        search_sort_layout.addWidget(self.cancel_button)
        search_sort_layout.addWidget(self.refresh_button)
        # QTableWidget for Customer Accounts
        self.customers_table = QTableWidget()
        self.tab_widget = QTabWidget()
        customer_table_tab = QWidget()
        self.customers_table.setColumnCount(5) 
        self.customers_table.setHorizontalHeaderLabels(["Username", "First Name", "Last Name", "Birth Number", "Address"])
        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        customer_table_layout = QVBoxLayout(customer_table_tab)
        customer_table_layout.addWidget(self.customers_table)
        self.tab_widget.addTab(customer_table_tab, "Customer Table")
        # GroupBox for Borrowed Books, Show History, Assign Book, Remove Book
        group_box_3 = QGroupBox("Books Actions")
        books_actions_layout = QVBoxLayout(group_box_3)
        self.show_borrowed_button = QPushButton("Show Borrowed Books")
        self.show_history_button = QPushButton("Show Customer History")
        self.assign_book_button = QPushButton("Assign a Book")
        self.remove_book_button = QPushButton("Remove Book")
        books_actions_layout.addWidget(self.show_borrowed_button)
        books_actions_layout.addWidget(self.show_history_button)
        books_actions_layout.addWidget(self.assign_book_button)
        books_actions_layout.addWidget(self.remove_book_button)
        # GroupBox for Add Account, Edit Account, Ban Account
        group_box_4 = QGroupBox("Account Actions")
        account_actions_layout = QVBoxLayout(group_box_4)
        self.add_account_button = QPushButton("Add Account")
        self.edit_account_button = QPushButton("Edit Account")
        self.ban_account_button = QPushButton("Ban Account")
        account_actions_layout.addWidget(self.add_account_button)
        account_actions_layout.addWidget(self.edit_account_button)
        account_actions_layout.addWidget(self.ban_account_button)
        # Set max height
        group_box_2.setMaximumHeight(100)
        # Add widgets to main layout
        left_layout.addWidget(self.tab_widget)
        right_layout.addWidget(group_box_1)
        right_layout.addWidget(group_box_2)
        right_layout.addWidget(group_box_3)
        right_layout.addWidget(group_box_4)
        # Layout Margins
        left_layout.setContentsMargins(15, 15, 7, 15)
        right_layout.setContentsMargins(8, 30, 15, 15)
        # Main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
        
    def display_customers(self):
        users_collection = self.database_manager.db["users"]
        # Query customers based on the role
        customer_query = {"role": "Customer"}
        customer_data = users_collection.find(customer_query)
        self.customers_table.setRowCount(0)
        for index, customer in enumerate(customer_data):
            self.customers_table.insertRow(index)
            for col, prop in enumerate(["username", "first_name", "last_name", "ssn", "address"]):
                self.customers_table.setItem(index, col, QTableWidgetItem(str(customer[prop])))
        self.customers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def register_user(self):
        dialog = RegistrationDialog()
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            create_account(self, dialog.username_signup.text(), dialog.password_signup.text(), "Librarian", dialog.first_name_signup.text(), dialog.last_name_signup.text(), dialog.ssn_signup.text(), dialog.address_signup.text(), self.statusBar)
            self.display_customers()