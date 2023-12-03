from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QDialog,
      QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from pathlib import Path
from datetime import datetime, timedelta , timezone
from PyQt6.QtCore import QTimer
import os
import pymongo
from database_manager import DatabaseManager
from advanced_search_dialog import AdvancedSearchDialog
from global_state import GlobalState


class CustomerTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__() 
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_customer_ui()
        # Signals
        self.signals.customer_tab_state.connect(self.set_tab_state)
        self.signals.customer_logged_in.connect(self.init_customer_tab)
        # Connects
        self.borrow_button.clicked.connect(self.borrow_book)
        self.return_button.clicked.connect(self.return_book)
        self.refresh_catalog_button.clicked.connect(lambda: self.display_book_catalog())
        self.advanced_search_button.clicked.connect(self.show_advanced_search_dialog)
        self.cancel_search_button.clicked.connect(self.cancel_search)
        # QTimer for updating every 10 seconds
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_borrowed_books)
        self.update_timer.start(10000)

    def init_customer_tab(self):
        self.display_book_catalog()
        self.display_borrowed_books()
        self.display_book_history()

    def update_borrowed_books(self):
        self.display_borrowed_books()

    def create_customer_ui(self):
        # Layout for the entire Customer tab
        layout = QVBoxLayout()
        # Top layout for "Advanced Search" and "Edit Profile" buttons
        top_layout = QHBoxLayout()
        self.advanced_search_button = QPushButton("Advanced Search")
        self.advanced_search_button.setEnabled(False)
        self.cancel_search_button = QPushButton("Cancel Search")
        self.cancel_search_button.setEnabled(False)
        self.edit_profile_button = QPushButton("Edit Profile")
        self.edit_profile_button.setEnabled(False)
        top_layout.addWidget(self.advanced_search_button)
        top_layout.addWidget(self.cancel_search_button)
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
        # Add code to populate catalog_table with data from MongoDB
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

    def set_tab_state(self, state):
        # Disable/enable widgets in customer_tab depending on whether the user is logged in or not
        self.edit_profile_button.setEnabled(state)
        self.advanced_search_button.setEnabled(state)
        self.borrow_button.setEnabled(state)
        self.return_button.setEnabled(state)
        self.refresh_catalog_button.setEnabled(state)
        self.tab_widget.setEnabled(state)
        if state == False: 
            self.catalog_table.setRowCount(0)    # Clearing the content of the book catalog
            self.borrowed_books_table.setRowCount(0) 
            self.tab_widget.setCurrentIndex(0)    # Displaying the catalog tab

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

    def borrow_book(self):
        # Get the selected row
        selected_row = self.catalog_table.currentRow()
        number_of_selected_rows = len(self.catalog_table.selectionModel().selectedRows())
        if number_of_selected_rows == 1:
            # Get book information from the selected row
            title = self.catalog_table.item(selected_row, 0).text()
            author = self.catalog_table.item(selected_row, 1).text()
            # Check if there are items available for borrowing
            items = int(self.catalog_table.item(selected_row, 4).text()) 
            if items <= 0:
                QMessageBox.warning(self, "Borrow Failed", f"The book '{title}' by {author} is out of stock.")
                return
            # Check if the user has reached the maximum limit of borrowed books (6 books)
            elif self.is_max_books_borrowed():
                QMessageBox.warning(self, "Book Limit Exceeded", "You have already borrowed the maximum allowed number of books (6).")
                return
            # Check if the book is already in the user's borrowed_books
            elif self.is_book_already_borrowed(title, author):
                QMessageBox.warning(self, "Already Borrowed", f"You have already borrowed '{title}' by {author}.")
                return
            # Confirm borrowing with the user
            else:
                reply = QMessageBox.question(
                    self,
                    "Borrow Book",
                    f"Do you want to borrow '{title}' by {author}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel
                )
                if reply == QMessageBox.StandardButton.Yes:
                    # Borrow the book
                    self.borrow_selected_book(selected_row)
                    # Add the book into the borrowed_books table
                    self.display_borrowed_books()
                    # Add the book information into the user's history
                    self.display_book_history()
        else:
            return

    def borrow_selected_book(self, selected_row):
        # Get book information from the selected row
        title = self.catalog_table.item(selected_row, 0).text()
        author = self.catalog_table.item(selected_row, 1).text()
        username = GlobalState.current_user
        # Insert a document into the 'borrowed_books' collection
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        borrowed_date = datetime.now(timezone.utc)
        expiry_date = borrowed_date + timedelta(minutes = 1)
        borrowed_book = {
            "username": username,
            "title": title,
            "author" : author,
            "borrowed_date": borrowed_date,
            "expiry_date": expiry_date
        }
        borrowed_books_collection.insert_one(borrowed_book)
        # Update the 'items' field in the 'books' collection (decrement by 1)
        books_collection = self.database_manager.db["books"]
        book_query = {"title": title, "author": author}
        update_query = {"$inc": {"items": -1}}
        books_collection.update_one(book_query, update_query)
        # Inform the user that the book has been borrowed
        self.statusBar.showMessage(f"You have borrowed '{title}' by {author}.", 7000)
        # Add the book to the user's history
        self.add_to_user_history(title, author, borrowed_date)

    def is_book_already_borrowed(self, title, author):
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        existing_borrowed_book = borrowed_books_collection.find_one(
            {"username": GlobalState.current_user, "title": title, "author": author}
        )
        return existing_borrowed_book is not None

    def is_max_books_borrowed(self):
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        borrowed_books_count = borrowed_books_collection.count_documents(
            {"username": GlobalState.current_user}
        )
        return borrowed_books_count >= 6

    def display_borrowed_books(self):
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        user_borrowed_books = borrowed_books_collection.find({"username": GlobalState.current_user})
        self.borrowed_books_table.setRowCount(0)
        for index, borrowed_book in enumerate(user_borrowed_books):
                # Retrieve book information from the "books" collection
                books_collection = self.database_manager.db["books"]
                book_query = {"title": borrowed_book["title"], "author": borrowed_book["author"]}
                book = books_collection.find_one(book_query)
                # Insert a new row into the table
                self.borrowed_books_table.insertRow(index)
                # Display book information in the table
                for col, prop in enumerate(["title", "author", "pages", "year"]):
                    self.borrowed_books_table.setItem(index, col, QTableWidgetItem(str(book[prop])))
                # Display book cover image
                cover_label = QLabel()
                cover_path = os.path.join(Path(__file__).resolve().parent.parent, "book_covers", f"{book['image_name']}.png")
                if os.path.exists(cover_path):
                    pixmap = QPixmap(cover_path)
                    scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    cover_label.setPixmap(scaled_pixmap)
                    self.borrowed_books_table.setRowHeight(index, scaled_pixmap.height())
                    cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.borrowed_books_table.setCellWidget(index, 4, cover_label)
                else:
                    placeholder_label = QLabel("No Image")
                    self.borrowed_books_table.setCellWidget(index, 4, placeholder_label)
                # Display the borrowed date in the sixth column
                borrowed_date = borrowed_book["borrowed_date"]
                formatted_borrowed_date = datetime.strftime(borrowed_date, "%d/%m/%Y, %H:%M")
                self.borrowed_books_table.setItem(index, 5, QTableWidgetItem(formatted_borrowed_date))
                # Display the expiration date in the seventh column
                expiry_date = borrowed_book["expiry_date"]
                formatted_expiry_date = datetime.strftime(expiry_date, "%d/%m/%Y, %H:%M")
                self.borrowed_books_table.setItem(index, 6, QTableWidgetItem(formatted_expiry_date))
        self.borrowed_books_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def return_book(self):
        selected_row = self.tab_widget.widget(1).layout().itemAt(0).widget().currentRow()
        number_of_selected_rows = len(self.tab_widget.widget(1).layout().itemAt(0).widget().selectionModel().selectedRows())
        if number_of_selected_rows == 1:
            # Get book information from the selected row
            title = self.tab_widget.widget(1).layout().itemAt(0).widget().item(selected_row, 0).text()
            author = self.tab_widget.widget(1).layout().itemAt(0).widget().item(selected_row, 1).text()
            # Confirm returning with the user
            reply = QMessageBox.question(
                self,
                "Return Book",
                f"Do you want to return '{title}' by {author}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Return the book
                self.return_selected_book(selected_row)
        else:
            return

    def return_selected_book(self, selected_row):
        # Get book information from the selected row
        title = self.tab_widget.widget(1).layout().itemAt(0).widget().item(selected_row, 0).text()
        author = self.tab_widget.widget(1).layout().itemAt(0).widget().item(selected_row, 1).text()
        # Remove the document from the 'borrowed_books' collection
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        return_query = {"username": GlobalState.current_user, "title": title, "author": author}
        borrowed_books_collection.delete_one(return_query)
        # Inform the user that the book has been returned
        self.statusBar.showMessage(f"You have returned '{title}' by {author}.", 5000)
        # Refresh the borrowed_books table
        self.display_borrowed_books()

    def add_to_user_history(self, title, author, event_date):
        # Add the book information into the user's history
        history_collection = self.database_manager.db["history"]
        history_entry = {
            "username": GlobalState.current_user,
            "title": title,
            "author": author,
            "event_date": event_date
        }
        history_collection.insert_one(history_entry)

    def display_book_history(self):
        # Display the user's book history in the history_table
        history_collection = self.database_manager.db["history"]
        user_history = history_collection.find({"username": GlobalState.current_user})
        self.history_table.setRowCount(0)
        for index, history_entry in enumerate(user_history):
            self.history_table.insertRow(index)
            for col, prop in enumerate(["title", "author", "pages", "year"]):
                # Retrieve book information from the "books" collection
                books_collection = self.database_manager.db["books"]
                book_query = {"title": history_entry["title"], "author": history_entry["author"]}
                book = books_collection.find_one(book_query)
                self.history_table.setItem(index, col, QTableWidgetItem(str(book[prop])))
            # Display book cover image
            cover_label = QLabel()
            cover_path = os.path.join(Path(__file__).resolve().parent.parent, "book_covers", f"{book['image_name']}.png")
            if os.path.exists(cover_path):
                pixmap = QPixmap(cover_path)
                scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                cover_label.setPixmap(scaled_pixmap)
                self.history_table.setRowHeight(index, scaled_pixmap.height())
                cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.history_table.setCellWidget(index, 4, cover_label)
            else:
                placeholder_label = QLabel("No Image")
                self.history_table.setCellWidget(index, 4, placeholder_label)
            # Display the event date in the fifth column
            formatted_event_date = datetime.strftime(history_entry["event_date"], "%d/%m/%Y, %H:%M")
            self.history_table.setItem(index, 5, QTableWidgetItem(formatted_event_date))
        self.history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def show_advanced_search_dialog(self):
        dialog = AdvancedSearchDialog()
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            # Retrieve user input from the dialog
            search_mode = dialog.search_radio.isChecked()
            author_text = dialog.author_input.text()
            title_text = dialog.title_input.text()
            year_text = dialog.year_input.text()
            self.search_and_sort_catalog(search_mode, author_text, title_text, year_text)

    def search_and_sort_catalog(self, search_mode, author_text, title_text, year_text):
        books_collection = self.database_manager.db["books"]
        author_formatted = ""
        title_formatted = ""
        year_formatted = ""
        if search_mode:
            query = {}
            if len(author_text) >= 3:
                query["author"] = {"$regex": author_text, "$options": "i"}
                author_formatted =(f"  Author: '{author_text}'")
            if len(title_text) >= 3:
                query["title"] = {"$regex": title_text, "$options": "i"}
                title_formatted =(f"  Title: '{title_text}'")
            if len(year_text) >= 3:
                query["year"] = {"$eq": int(year_text)}
                year_formatted =(f"  Year: '{year_text}'")
            if len(author_text) >= 3 or len(title_text) >= 3 or len(year_text) >= 3:
                self.signals.update_status_bar_widget.emit(f"Showing searches for: {author_formatted}{title_formatted}{year_formatted}")
                self.refresh_catalog_button.setEnabled(False)   # Disabling the button to refresh search results
                self.cancel_search_button.setEnabled(True)    # Disable the button to cancel the search if the search is not in progress
                cursor = books_collection.find(query)
                self.display_book_catalog(cursor)
            else:
                self.statusBar.showMessage("The minimum character length required for searching/sorting is 3.", 5000)
                return
        else:
            sort_criteria = []
            if len(author_text) >= 3:
                sort_criteria.append(("author", pymongo.ASCENDING))
                author_formatted =(f"  Author: '{author_text}'")
            if len(title_text) >= 3:
                sort_criteria.append(("title", pymongo.ASCENDING))
            if len(year_text) >= 3:
                sort_criteria.append(("year", pymongo.ASCENDING))
                title_formatted =(f"  Title: '{title_text}'")
                year_formatted =(f"  Year: '{year_text}'")
            if len(author_text) >= 3 or len(title_text) >= 3 or len(year_text) >= 3:
                self.signals.update_status_bar_widget.emit(f"Sorted by: {author_formatted}{title_formatted}{year_formatted}")
                self.refresh_catalog_button.setEnabled(False)  
                self.cancel_search_button.setEnabled(True)    
                cursor = books_collection.find().sort(sort_criteria)
                self.display_book_catalog(cursor)
            else:
                self.statusBar.showMessage("The minimum character length required for searching/sorting is 3.", 5000)
                return

    def cancel_search(self):
        self.refresh_catalog_button.setEnabled(True)
        self.cancel_search_button.setEnabled(False) 
        self.signals.update_status_bar_widget.emit("")
        self.display_book_catalog()