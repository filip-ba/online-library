from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, 
      QHBoxLayout, QTableWidget, QDialog )
from database_manager import DatabaseManager
from dialogs.add_book_dialog import AddBookDialog
from shared_functions import display_book_catalog
from shared_functions import advanced_search
from shared_functions import sort_book_catalog


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
        self.refresh_catalog_button.clicked.connect(lambda: self.display_books())
        self.advanced_search_button.clicked.connect(self.search_books)
        self.cancel_button.clicked.connect(self.cancel_search_or_sort)
        self.sort_books_button.clicked.connect(self.sort_books)
        self.add_book_button.clicked.connect(self.show_add_book_dialog)
        self.delete_book_button.clicked.connect(self.delete_selected_book)

    def init_librarian_tab(self):
        self.display_books()

    def set_tab_state(self, state):
        # Disable/enable widgets in customer_tab depending on whether the user is logged in or not
        self.advanced_search_button.setEnabled(state)
        self.sort_books_button.setEnabled(state)
        self.cancel_button.setEnabled(state)
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
        self.advanced_search_button = QPushButton("Advanced Search")
        self.advanced_search_button.setEnabled(False)
        self.sort_books_button = QPushButton("Sort Books")
        self.sort_books_button.setEnabled(False)
        self.cancel_button = QPushButton("Cancel Search/Sort")
        self.cancel_button.setEnabled(False)
        self.refresh_catalog_button = QPushButton("Refresh Catalog")
        self.refresh_catalog_button.setEnabled(False)
        top_layout.addWidget(self.advanced_search_button)
        top_layout.addWidget(self.sort_books_button)
        top_layout.addWidget(self.cancel_button)
        top_layout.addWidget(self.refresh_catalog_button)
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
            image_name = dialog.image_input.text()
            # Validate that all fields are filled
            if not title or not author or not year or not image_name:
                QMessageBox.warning(self, "Incomplete Information", "All fields must be filled in.")
                return
            self.add_new_book(title, author, pages, year, items, image_name)

    def add_new_book(self, title, author, pages, year, items, image_name):
        books_collection = self.database_manager.db["books"]
        new_book = {
            "title": title,
            "author": author,
            "pages": pages,
            "year": year,
            "items": items,
            "image_name": image_name
        }
        books_collection.insert_one(new_book)
        self.display_books()



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
        self.display_books()

    def is_book_borrowed(self, title, author):
        # Check if the book is in the borrowed_books collection
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        borrowed_book = borrowed_books_collection.find_one({"title": title, "author": author})
        return borrowed_book is not None
    

