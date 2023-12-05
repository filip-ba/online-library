from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QComboBox, QListView, QSpacerItem, QSizePolicy,  
      QInputDialog, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QGroupBox, QGridLayout )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from bson import ObjectId
from pathlib import Path
import os
from global_state import GlobalState
from datetime import datetime, timedelta , timezone
from database_manager import DatabaseManager


class ManageConfirmationsTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_tab_ui()
        # Connects

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
        search_button = QPushButton("Open Search")
        sort_button = QPushButton("Open Sort Options")
        cancel_button = QPushButton("Cancel Search/Sort")
        refresh_button = QPushButton("Refresh List")
        search_sort_layout.addWidget(search_button)
        search_sort_layout.addWidget(sort_button)
        search_sort_layout.addWidget(cancel_button)
        search_sort_layout.addWidget(refresh_button)
        # QTableWidget for Customer Accounts
        table_widget = QTableWidget()
        # GroupBox for Borrowed Books, Show History, Assign Book, Remove Book
        group_box_3 = QGroupBox("Books Actions")
        books_actions_layout = QVBoxLayout(group_box_3)
        show_borrowed_button = QPushButton("Show Borrowed Books")
        show_history_button = QPushButton("Show Customer History")
        assign_book_button = QPushButton("Assign a Book")
        remove_book_button = QPushButton("Remove Book")
        books_actions_layout.addWidget(show_borrowed_button)
        books_actions_layout.addWidget(show_history_button)
        books_actions_layout.addWidget(assign_book_button)
        books_actions_layout.addWidget(remove_book_button)
        # GroupBox for Add Account, Edit Account, Ban Account
        group_box_4 = QGroupBox("Account Actions")
        account_actions_layout = QVBoxLayout(group_box_4)
        add_account_button = QPushButton("Add Account")
        edit_account_button = QPushButton("Edit Account")
        ban_account_button = QPushButton("Ban Account")
        account_actions_layout.addWidget(add_account_button)
        account_actions_layout.addWidget(edit_account_button)
        account_actions_layout.addWidget(ban_account_button)
        # Add widgets to main layout
        left_layout.addWidget(table_widget)
        right_layout.addWidget(group_box_1)
        right_layout.addWidget(group_box_2)
        right_layout.addWidget(group_box_3)
        right_layout.addWidget(group_box_4)
        # main layout
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)
