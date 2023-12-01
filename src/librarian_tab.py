from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QComboBox,  
      QInputDialog, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from bson import ObjectId
from pathlib import Path
import os
from database_manager import DatabaseManager
from global_state import GlobalState
from datetime import datetime, timedelta , timezone


class LibrarianTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_librarian_ui()
        # Singals
        self.signals.librarian_tab_state.connect(self.set_tab_state)
        self.signals.librarian_logged_in.connect(self.init_librarian_tab)
        # Connects

    def init_librarian_tab(self):
        pass

    def set_tab_state(self, state):
        # Disable/enable widgets in customer_tab depending on whether the user is logged in or not
        if state == False: 
            pass

    def create_librarian_ui(self):
        # Layout for the entire Librarian tab
        layout = QVBoxLayout()
        # Top layout for various functionalities
        top_layout = QHBoxLayout()
        self.add_book_button = QPushButton("Add Book")
        self.edit_book_button = QPushButton("Edit Book")
        self.delete_book_button = QPushButton("Delete Book")
        self.add_user_button = QPushButton("Add User")
        self.edit_user_button = QPushButton("Edit User")
        self.approve_account_button = QPushButton("Approve Account")
        self.ban_account_button = QPushButton("Ban Account")
        self.check_out_book_button = QPushButton("Check Out Book")
        self.assign_book_button = QPushButton("Assign Book")
        top_layout.addWidget(self.add_book_button)
        top_layout.addWidget(self.edit_book_button)
        top_layout.addWidget(self.delete_book_button)
        top_layout.addWidget(self.add_user_button)
        top_layout.addWidget(self.edit_user_button)
        top_layout.addWidget(self.approve_account_button)
        top_layout.addWidget(self.ban_account_button)
        top_layout.addWidget(self.check_out_book_button)
        top_layout.addWidget(self.assign_book_button)
        # Middle layout for the QTabWidget
        tab_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.tab_widget.setEnabled(False)
        books_tab = QWidget()
        users_tab = QWidget()
        # Layout for the Books tab
        books_layout = QVBoxLayout(books_tab)
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(6)
        self.books_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Items", "Book Cover"])
        books_layout.addWidget(self.books_table)
        # Layout for the Users tab
        users_layout = QVBoxLayout(users_tab)
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(7)
        self.users_table.setHorizontalHeaderLabels(["First Name", "Last Name", "Address", "Birth Number", "Username", "Account Activated", "Borrowing History"])
        users_layout.addWidget(self.users_table)
        # Add tabs to the QTabWidget
        self.tab_widget.addTab(books_tab, "Books")
        self.tab_widget.addTab(users_tab, "Users")
        tab_layout.addWidget(self.tab_widget)
        # Bottom layout for search, sort, import/export, and refresh
        bottom_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_line_edit = QLineEdit()
        search_by_label = QLabel("Search by:")
        self.search_by_combo = QComboBox()
        self.search_by_combo.addItems(["First Name", "Last Name", "Address", "Birth Number"])
        self.and_or_label = QLabel("AND/OR:")
        self.and_or_combo = QComboBox()
        self.and_or_combo.addItems(["AND", "OR"])
        self.sort_label = QLabel("Sort by:")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["First Name", "Last Name", "Address", "Birth Number"])
        self.search_button = QPushButton("Search")
        self.sort_button = QPushButton("Sort")
        self.import_data_button = QPushButton("Import Data")
        self.export_data_button = QPushButton("Export Data")
        self.refresh_button = QPushButton("Refresh")
        bottom_layout.addWidget(search_label)
        bottom_layout.addWidget(self.search_line_edit)
        bottom_layout.addWidget(search_by_label)
        bottom_layout.addWidget(self.search_by_combo)
        bottom_layout.addWidget(self.and_or_label)
        bottom_layout.addWidget(self.and_or_combo)
        bottom_layout.addWidget(self.sort_label)
        bottom_layout.addWidget(self.sort_combo)
        bottom_layout.addWidget(self.search_button)
        bottom_layout.addWidget(self.sort_button)
        bottom_layout.addWidget(self.import_data_button)
        bottom_layout.addWidget(self.export_data_button)
        bottom_layout.addWidget(self.refresh_button)
        # Add layouts to the main layout
        layout.addLayout(top_layout)
        layout.addLayout(tab_layout)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def add_book(self):
        # Implement functionality to add a book
        pass

    def edit_book(self):
        # Implement functionality to edit a book
        pass

    def delete_book(self):
        # Implement functionality to delete a book
        pass

    def add_user(self):
        # Implement functionality to add a user
        pass

    def edit_user(self):
        # Implement functionality to edit a user
        pass

    def approve_account(self):
        # Implement functionality to approve a user's account
        pass

    def ban_account(self):
        # Implement functionality to ban a user's account
        pass

    def check_out_book(self):
        # Implement functionality to check out a book
        pass

    def assign_book(self):
        # Implement functionality to assign a book to a user
        pass

    def search_users(self):
        # Implement functionality to search users
        pass

    def sort_users(self):
        # Implement functionality to sort users
        pass

    def import_data(self):
        # Implement functionality to import data
        pass

    def export_data(self):
        # Implement functionality to export data
        pass

    def load_tables(self):
        # Implement functionality to load tables
        pass

