from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, 
      QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path
import os
from global_state import GlobalState
from database_manager import DatabaseManager


class ManageBooksTab(QWidget):
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
        self.delete_book_button.clicked.connect(self.delete_selected_book)

    def init_librarian_tab(self):
        self.display_book_catalog()

    def set_tab_state(self, state):
        # Disable/enable widgets in customer_tab depending on whether the user is logged in or not
        self.assign_book_button.setEnabled(state)
        self.sort_books_button.setEnabled(state)
        self.edit_profile_button.setEnabled(state)
        self.add_book_button.setEnabled(state)
        self.edit_book_button.setEnabled(state)
        self.delete_book_button.setEnabled(state)
        self.tab_widget.setEnabled(state)
        if state == False: 
            self.catalog_table.setRowCount(0)    
            self.tab_widget.setCurrentIndex(0)    

    def create_tab_ui(self):
        # Layout for the entire Customer tab
        layout = QVBoxLayout()
        # Top layout for "Advanced Search" and "Edit Profile" buttons
        top_layout = QHBoxLayout()
        self.assign_book_button = QPushButton("Assign a Book")
        self.assign_book_button.setEnabled(False)
        self.sort_books_button = QPushButton("Sort Books")
        self.sort_books_button.setEnabled(False)
        self.cancel_button = QPushButton("Cancel Search/Sort")
        self.cancel_button.setEnabled(False)
        self.edit_profile_button = QPushButton("Edit Profile")
        self.edit_profile_button.setEnabled(False)
        top_layout.addWidget(self.assign_book_button)
        top_layout.addWidget(self.sort_books_button)
        top_layout.addWidget(self.cancel_button)
        top_layout.addWidget(self.edit_profile_button)
        # Middle layout for the QTabWidget
        tab_layout = QHBoxLayout()
        self.tab_widget = QTabWidget()
        self.tab_widget.setEnabled(False)
        catalog_tab = QWidget()
        # Layout for the Catalog tab
        catalog_layout = QVBoxLayout(catalog_tab)
        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(6) 
        self.catalog_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Items", "Book Cover"])
        catalog_layout.addWidget(self.catalog_table)
        # Add tabs to the QTabWidget
        self.tab_widget.addTab(catalog_tab, "Book Catalog")
        tab_layout.addWidget(self.tab_widget)
        # Bottom layout for "Borrow" and "Return" buttons
        bottom_layout = QHBoxLayout()
        self.add_book_button = QPushButton("Add Book")
        self.add_book_button.setEnabled(False)
        self.edit_book_button = QPushButton("Edit Book")
        self.edit_book_button.setEnabled(False)
        self.delete_book_button = QPushButton("Delete Book")
        self.delete_book_button.setEnabled(False)
        bottom_layout.addWidget(self.add_book_button)
        bottom_layout.addWidget(self.edit_book_button)
        bottom_layout.addWidget(self.delete_book_button)
        # Add layouts to the main layout
        layout.addLayout(top_layout)
        layout.addLayout(tab_layout)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def display_book_catalog(self, cursor=None):
        if cursor is None:
            books_collection = self.database_manager.db["books"]
            cursor = books_collection.find()
        self.catalog_table.setRowCount(0)
        for index, book in enumerate(cursor):
            self.catalog_table.insertRow(index)
            self.catalog_table.setItem(index, 0, QTableWidgetItem(book["title"]))
            self.catalog_table.setItem(index, 1, QTableWidgetItem(book["author"]))
            self.catalog_table.setItem(index, 2, QTableWidgetItem(str(book["pages"])))
            self.catalog_table.setItem(index, 3, QTableWidgetItem(str(book["year"])))
            self.catalog_table.setItem(index, 4, QTableWidgetItem(str(book["items"])))
            # Display book cover image
            cover_label = QLabel()
            # Construct the absolute path to the book cover image
            cover_path = os.path.join(Path(__file__).resolve().parent.parent, "book_covers", f"{book['image_name']}.png")
            # Check if the file exists before attempting to load
            if os.path.exists(cover_path):
                pixmap = QPixmap(cover_path)
                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                cover_label.setPixmap(scaled_pixmap)
                # Set the row height dynamically based on the image height
                self.catalog_table.setRowHeight(index, scaled_pixmap.height())
                # Set the alignment of the image within the cell
                cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.catalog_table.setCellWidget(index, 5, cover_label)  
            else:
                placeholder_label = QLabel("No Image")
                self.catalog_table.setCellWidget(index, 5, placeholder_label) 
        # Set the whole table as read-only
        self.catalog_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def delete_selected_book(self):
        selected_row = self.catalog_table.currentRow()
        number_of_selected_rows = len(self.catalog_table.selectionModel().selectedRows())
        if number_of_selected_rows == 1:
            title = self.catalog_table.item(selected_row, 0).text()
            author = self.catalog_table.item(selected_row, 1).text()
            # Check if the book has been borrowed
            if self.is_book_borrowed(title, author):
                QMessageBox.warning(self, "Deletion Failed", f"The book '{title}' by {author} has been borrowed and cannot be deleted.")
                return
            # Confirm deletion with the user
            reply = QMessageBox.question(
                self,
                "Delete Book",
                f"Do you want to delete '{title}' by {author}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.delete_book(title, author)

    def delete_book(self, title, author):
        # Delete the book from the 'books' collection
        books_collection = self.database_manager.db["books"]
        book_query = {"title": title, "author": author}
        books_collection.delete_one(book_query)
        self.statusBar.showMessage(f"The book '{title}' by {author} has been deleted.", 5000)
        self.display_book_catalog()

    def is_book_borrowed(self, title, author):
        # Check if the book is in the borrowed_books collection
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        borrowed_book = borrowed_books_collection.find_one({"title": title, "author": author})
        return borrowed_book is not None
