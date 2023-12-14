from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, 
      QHBoxLayout, QTableWidget, QDialog, QHeaderView, QAbstractItemView )
from pathlib import Path
import shutil
import os
from database_manager import DatabaseManager
from dialogs.add_book_dialog import AddBookDialog
from shared_functions import display_book_catalog
from shared_functions import advanced_search
from shared_functions import sort_book_catalog
from dialogs.edit_book_dialog import EditBookDialog


class ManageBooksTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_tab_ui()
        # Singals
        self.signals.librarian_logged_in.connect(self.init_librarian_tab)
        # Connects
        self.refresh_catalog_button.clicked.connect(lambda: self.display_books())
        self.advanced_search_button.clicked.connect(self.search_books)
        self.sort_books_button.clicked.connect(self.sort_books)
        self.cancel_button.clicked.connect(self.cancel_search_or_sort)
        self.add_book_button.clicked.connect(self.show_add_book_dialog)
        self.edit_book_button.clicked.connect(self.show_edit_book_dialog)
        self.delete_book_button.clicked.connect(self.delete_selected_book)

    def init_librarian_tab(self):
        self.display_books() 
        self.cancel_button.setEnabled(False)
        self.refresh_catalog_button.setEnabled(True)    

    def create_tab_ui(self):
        # Layout for the entire Customer tab
        layout = QVBoxLayout()
        # Top layout for "Advanced Search" and "Edit Profile" buttons
        top_layout = QHBoxLayout()
        self.advanced_search_button = QPushButton("Open Search")
        self.sort_books_button = QPushButton("Open Sort Options")
        self.cancel_button = QPushButton("Cancel Selected Filters")
        self.refresh_catalog_button = QPushButton("Refresh Catalog")
        top_layout.addWidget(self.advanced_search_button)
        top_layout.addWidget(self.sort_books_button)
        top_layout.addWidget(self.cancel_button)
        top_layout.addWidget(self.refresh_catalog_button)
        # Middle layout for the QTabWidget
        tab_layout = QHBoxLayout()
        self.tab_widget = QTabWidget()
        catalog_tab = QWidget()
        # Layout for the Catalog tab
        catalog_layout = QVBoxLayout(catalog_tab)
        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(6) 
        self.catalog_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Items", "Book Cover"])
        self.catalog_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.catalog_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        catalog_layout.addWidget(self.catalog_table)
        # Add tabs to the QTabWidget
        self.tab_widget.addTab(catalog_tab, "Book Catalog")
        tab_layout.addWidget(self.tab_widget)
        # Bottom layout for "Borrow" and "Return" buttons
        bottom_layout = QHBoxLayout()
        self.add_book_button = QPushButton("Add Book")
        self.edit_book_button = QPushButton("Edit Book")
        self.delete_book_button = QPushButton("Delete Book")
        bottom_layout.addWidget(self.add_book_button)
        bottom_layout.addWidget(self.edit_book_button)
        bottom_layout.addWidget(self.delete_book_button)
        # Add layouts to the main layout
        top_layout.setContentsMargins(15, 15, 15, 7)
        tab_layout.setContentsMargins(15, 8, 15, 8)
        bottom_layout.setContentsMargins(15, 7, 15, 15)
        layout.addLayout(top_layout)
        layout.addLayout(tab_layout)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def display_books(self, cursor=None):
        display_book_catalog(self, self.catalog_table, cursor)

    def search_books(self):
        advanced_search(self, self.signals, self.statusBar, self.catalog_table, self.refresh_catalog_button, self.cancel_button)

    def sort_books(self):
        sort_book_catalog(self, self.signals, self.catalog_table, self.refresh_catalog_button, self.cancel_button)

    def cancel_search_or_sort(self):
        self.refresh_catalog_button.setEnabled(True)
        self.cancel_button.setEnabled(False) 
        self.signals.update_status_bar_widget.emit("")
        self.display_books()

    def show_add_book_dialog(self):
        dialog = AddBookDialog()
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            # Retrieve user input from the dialog
            title = dialog.title_input.text()
            author = dialog.author_input.text()
            pages = dialog.pages_input.text()
            year = dialog.year_input.text()
            items = dialog.items_input.text()
            full_image_name = dialog.path_name
            image_name = dialog.image_name 
            # Validate that all fields are filled
            if not title or not author or not pages or not year or not items or not image_name:
                QMessageBox.warning(self, "Incomplete Information", "All fields must be filled in.")
                return
            else:
                destination_folder = Path(__file__).resolve().parent.parent.parent / "book_covers"
                destination_path = str(destination_folder / os.path.basename(full_image_name))
                if os.path.exists(destination_path):
                    QMessageBox.warning(self, "File Exists", "An image with the same name already exists. Please choose a different name.")
                    return
                else:
                    shutil.copy(full_image_name, destination_path)
                    self.add_new_book(title, author, pages, year, items, image_name)

    def add_new_book(self, title, author, pages, year, items, image_name):
        books_collection = self.database_manager.db["books"]
        new_book = {
            "title": title,
            "author": author,
            "pages": int(pages),
            "year": year,
            "items": int(items),
            "image_name": image_name
        }
        books_collection.insert_one(new_book)
        self.statusBar.showMessage(f"You have added a book '{title}' by {author}.", 8000)
        self.display_books()

    def show_edit_book_dialog(self):
        selected_row = self.catalog_table.currentRow()
        number_of_selected_rows = len(self.catalog_table.selectionModel().selectedRows())
        if number_of_selected_rows == 1:
            # Get title and author from the selected row
            current_title = self.catalog_table.item(selected_row, 0).text()
            current_author = self.catalog_table.item(selected_row, 1).text()
            # Retrieve book data from the database based on title and author
            books_collection = self.database_manager.db["books"]
            query = {"title": current_title, "author": current_author}
            book_data = books_collection.find_one(query)
            dialog = EditBookDialog(book_data)
            result = dialog.exec()
        else:
            return
        if result == QDialog.DialogCode.Accepted:
            title_text = dialog.title_input.text()
            author_text = dialog.author_input.text()
            pages_text = dialog.pages_input.text()
            year_text = dialog.year_input.text()
            items_text = dialog.items_input.text()
            title = title_text if title_text else None
            author = author_text if author_text else None
            pages = int(pages_text) if pages_text else None
            year = year_text if year_text else None
            items = int(items_text) if items_text else None
            edited_data = {
                "title": title,
                "author": author,
                "pages": pages,
                "year": year,
                "items": items,
            }
            # Validate that all fields are filled
            if None in edited_data.values():
                QMessageBox.warning(self, "Incomplete Information", "All fields must be filled in.")
                return
            # Show a status bar message
            self.statusBar.showMessage(f"You have edited '{current_title}' by {current_author}.", 8000)
            # Call a function to update the book information
            self.edit_book(book_data, edited_data)

    def edit_book(self, old_data, new_data):
        books_collection = self.database_manager.db["books"]
        # Construct a query to find the book with old_data
        query = {
            "title": old_data["title"],
            "author": old_data["author"],
            "pages": old_data["pages"],
            "year": old_data["year"],
            "items": old_data["items"],
            "image_name": old_data["image_name"]
        }
        # Set the new values
        update_values = {"$set": new_data}
        # Update the book with the new information
        books_collection.update_one(query, update_values)
        # Optionally, refresh the book catalog display
        self.display_books()

    def delete_selected_book(self):
        selected_row = self.catalog_table.currentRow()
        number_of_selected_rows = len(self.catalog_table.selectionModel().selectedRows())
        if number_of_selected_rows == 1:
            title = self.catalog_table.item(selected_row, 0).text()
            author = self.catalog_table.item(selected_row, 1).text()
            # Find the book_id
            books_collection = self.database_manager.db["books"]
            book_query = {"title": title, "author": author}
            book_document = books_collection.find_one(book_query)
            book_id = book_document["_id"]
            # Check if the book has been borrowed
            if self.is_book_borrowed(book_id):
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
        self.statusBar.showMessage(f"The book '{title}' by {author} has been deleted.", 8000)
        books_collection.delete_one(book_query)
        self.display_books()
           
    def is_book_borrowed(self, book_id):
        # Check if the book is in the borrowed_books collection
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        borrowed_book = borrowed_books_collection.find_one({"book_id": book_id})
        return borrowed_book is not None
    

