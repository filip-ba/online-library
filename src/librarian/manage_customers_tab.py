from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QComboBox, QListWidget, QSpacerItem, QScrollArea,  
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
        self.signals.librarian_logged_in.connect(self.init_librarian_tab)
        # Connects
        self.refresh_button.clicked.connect(self.display_customers)
        self.add_account_button.clicked.connect(self.register_user)

    def init_librarian_tab(self):
        self.display_customers()

    def create_tab_ui(self):
        # Layouts
        middle_layout = QVBoxLayout()
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        main_layout = QHBoxLayout()
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
        # Import/Export Layout
        group_box_2 = QGroupBox("Import/Export All Collections")
        group_box_2.setMaximumHeight(100)
        import_export_layout = QHBoxLayout(group_box_2)
        self.import_button = QPushButton("Import")
        self.export_button = QPushButton("Export")
        import_export_layout.addWidget(self.import_button)
        import_export_layout.addWidget(self.export_button)
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
        # QTableWidget for Customer Accounts
        self.customers_table = QTableWidget()
        self.tab_widget = QTabWidget()
        customer_table_tab = QWidget()
        self.customers_table.setColumnCount(5) 
        self.customers_table.setHorizontalHeaderLabels(["Username", "First Name", "Last Name", "SSN", "Address"])
        self.tab_widget.setMinimumWidth(375)
        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        customer_table_layout = QVBoxLayout(customer_table_tab)
        customer_table_layout.addWidget(self.customers_table)
        self.tab_widget.addTab(customer_table_tab, "Customer Table")
        # List Widget 1
        list_layout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.list_widget_activate_acc = QListWidget()
        list_title_1 = QLabel("Accounts to Activate")
        self.confirm_account_button = QPushButton("Confirm")
        self.decline_account_button = QPushButton("Decline")
        button_layout.addWidget(self.confirm_account_button)
        button_layout.addWidget(self.decline_account_button)
        list_layout.addWidget(list_title_1)
        list_layout.addWidget(self.list_widget_activate_acc)
        list_layout.addLayout(button_layout)
        # List Widget 2
        list_layout_2 = QVBoxLayout()
        button_layout_2 = QHBoxLayout()
        self.list_widget_confirm_changes = QListWidget()
        list_title__2 = QLabel("Confirm Account Changes")
        self.confirm_changes_button = QPushButton("Confirm")
        self.decline_cahnges_button = QPushButton("Decline")
        button_layout_2.addWidget(self.confirm_changes_button)
        button_layout_2.addWidget(self.decline_cahnges_button)
        list_layout_2.addWidget(list_title__2)
        list_layout_2.addWidget(self.list_widget_confirm_changes)
        list_layout_2.addLayout(button_layout_2)
        # Wrap the left_layout in a QScrollArea
        scroll_wrapper = QWidget()
        scroll_wrapper.setMinimumWidth(250)
        scroll_wrapper.setMaximumWidth(250)
        scroll_wrapper_layout = QVBoxLayout(scroll_wrapper)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff) 
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        scroll_area.setWidget(left_widget)
        scroll_wrapper_layout.addWidget(scroll_area)
        # Add widgets to main layout
        left_layout.addWidget(group_box_1)
        left_layout.addWidget(group_box_2)
        left_layout.addWidget(group_box_3)
        left_layout.addWidget(group_box_4)
        middle_layout.addWidget(self.tab_widget)
        right_layout.addLayout(list_layout)
        right_layout.addLayout(list_layout_2)
        # Layout Margins 
        scroll_wrapper_layout.setContentsMargins(15, 15, 7, 15)
        middle_layout.setContentsMargins(8, 15, 8, 15)
        right_layout.setContentsMargins(7, 15, 15, 15)
        # Main layout
        main_layout.addWidget(scroll_wrapper)
        main_layout.addLayout(middle_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

    def display_customers(self):
        users_collection = self.database_manager.db["users"]
        customer_data = users_collection.find()
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
            create_account(self, dialog.username_signup.text(), dialog.password_signup.text(), dialog.first_name_signup.text(), dialog.last_name_signup.text(), dialog.ssn_signup.text(), dialog.address_signup.text(), "Librarian", self.statusBar)
            self.display_customers()