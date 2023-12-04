from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QComboBox,  
      QInputDialog, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from bson import ObjectId
from pathlib import Path
import os
from global_state import GlobalState
from datetime import datetime, timedelta , timezone
from database_manager import DatabaseManager


class ManageCustomersTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_tab_ui()
        # Connects

    def create_tab_ui(self):
        # Layout for the entire Customer tab
        layout = QVBoxLayout()
        # Top layout for "Advanced Search" and "Edit Profile" buttons
        top_layout = QHBoxLayout()
        self.advanced_search_button = QPushButton("Advanced Search")
        self.advanced_search_button.setEnabled(False)
        self.sort_books_button = QPushButton("Sort Books")
        self.sort_books_button.setEnabled(False)
        self.cancel_button = QPushButton("Cancel Search/Sort")
        self.cancel_button.setEnabled(False)
        self.edit_profile_button = QPushButton("Edit Profile")
        self.edit_profile_button.setEnabled(False)
        top_layout.addWidget(self.advanced_search_button)
        top_layout.addWidget(self.sort_books_button)
        top_layout.addWidget(self.cancel_button)
        top_layout.addWidget(self.edit_profile_button)
        # Middle layout for the QTabWidget
        tab_layout = QHBoxLayout()
        self.tab_widget = QTabWidget()
        self.tab_widget.setEnabled(False)
        catalog_tab = QWidget()
        borrowed_books_tab = QWidget()
        history_tab = QWidget()
        # Layout for the Catalog tab
        catalog_layout = QVBoxLayout(catalog_tab)
        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(6) 
        self.catalog_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Items", "Book Cover"])
        catalog_layout.addWidget(self.catalog_table)
        # Layout for the Borrowed Books tab
        borrowed_books_layout = QVBoxLayout(borrowed_books_tab)
        self.borrowed_books_table = QTableWidget()
        self.borrowed_books_table.setColumnCount(7)
        self.borrowed_books_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Book Cover", "Borrow Date", "Due Date"])
        # Add code to populate borrowed_books_table with data from MongoDB
        borrowed_books_layout.addWidget(self.borrowed_books_table)
        # Layout for the History tab
        history_layout = QVBoxLayout(history_tab)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)  
        self.history_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Book Cover", "Date Borrowed"])
        # Add code to populate history_table with data from MongoDB
        history_layout.addWidget(self.history_table)
        # Add tabs to the QTabWidget
        self.tab_widget.addTab(catalog_tab, "Catalog")
        self.tab_widget.addTab(borrowed_books_tab, "Borrowed Books")
        self.tab_widget.addTab(history_tab, "History")
        tab_layout.addWidget(self.tab_widget)
        # Bottom layout for "Borrow" and "Return" buttons
        bottom_layout = QHBoxLayout()
        self.borrow_button = QPushButton("Borrow")
        self.borrow_button.setEnabled(False)
        self.return_button = QPushButton("Return")
        self.return_button.setEnabled(False)
        self.refresh_catalog_button = QPushButton("Refresh Catalog")
        self.refresh_catalog_button.setEnabled(False)
        bottom_layout.addWidget(self.borrow_button)
        bottom_layout.addWidget(self.return_button)
        bottom_layout.addWidget(self.refresh_catalog_button)
        # Add layouts to the main layout
        layout.addLayout(top_layout)
        layout.addLayout(tab_layout)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)