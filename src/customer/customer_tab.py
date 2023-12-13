from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QDialog,
      QHBoxLayout, QTableWidget, QHeaderView, QAbstractItemView )
from datetime import datetime, timedelta
import bcrypt  
from database_manager import DatabaseManager
from global_state import GlobalState
from shared_functions import display_book_catalog
from shared_functions import display_borrowed_books
from shared_functions import display_book_history
from shared_functions import advanced_search
from shared_functions import sort_book_catalog
from dialogs.edit_profile_dialog import EditProfileDialog


class CustomerTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__() 
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_customer_ui()
        # Signals
        self.signals.customer_logged_in.connect(self.init_customer_tab)
        # Connects
        self.refresh_catalog_button.clicked.connect(lambda: self.display_books())
        self.advanced_search_button.clicked.connect(self.search_books)
        self.cancel_button.clicked.connect(self.cancel_search_or_sort)
        self.sort_books_button.clicked.connect(self.sort_books)
        self.borrow_button.clicked.connect(self.borrow_book)
        self.return_button.clicked.connect(self.return_book)
        self.edit_profile_button.clicked.connect(self.edit_details)

    def init_customer_tab(self):
        self.display_books()
        self.display_borrowed_books()
        self.display_history()
        self.tab_widget.setCurrentIndex(0)
        self.cancel_button.setEnabled(False)
        self.refresh_catalog_button.setEnabled(True)

    def create_customer_ui(self):
        # Layout for the entire Customer tab
        layout = QVBoxLayout()
        # Top layout 
        top_layout = QHBoxLayout()
        self.advanced_search_button = QPushButton("Open Search")
        self.sort_books_button = QPushButton("Open Sort Options")
        self.cancel_button = QPushButton("Cancel Selected Filters")
        self.refresh_catalog_button = QPushButton("Refresh Catalog")
        top_layout.addWidget(self.advanced_search_button)
        top_layout.addWidget(self.sort_books_button)
        top_layout.addWidget(self.cancel_button)
        top_layout.addWidget(self.refresh_catalog_button)
        # Middle layout 
        tab_layout = QHBoxLayout()
        self.tab_widget = QTabWidget()
        catalog_tab = QWidget()
        borrowed_books_tab = QWidget()
        history_tab = QWidget()
        # Layout for the Catalog tab
        catalog_layout = QVBoxLayout(catalog_tab)
        self.catalog_table = QTableWidget()
        self.catalog_table.setColumnCount(6) 
        self.catalog_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Items", "Book Cover"])
        self.catalog_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        catalog_layout.addWidget(self.catalog_table)
        header = self.catalog_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Layout for the Borrowed Books tab
        borrowed_books_layout = QVBoxLayout(borrowed_books_tab)
        self.borrowed_books_table = QTableWidget()
        self.borrowed_books_table.setColumnCount(7)
        self.borrowed_books_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Book Cover", "Borrow Date", "Due Date"])
        self.borrowed_books_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.borrowed_books_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        borrowed_books_layout.addWidget(self.borrowed_books_table)
        # Layout for the History tab
        history_layout = QVBoxLayout(history_tab)
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)  
        self.history_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Book Cover", "Date Borrowed"])
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        history_layout.addWidget(self.history_table)
        # Add tabs to the QTabWidget
        self.tab_widget.addTab(catalog_tab, "Catalog")
        self.tab_widget.addTab(borrowed_books_tab, "Borrowed Books")
        self.tab_widget.addTab(history_tab, "History")
        tab_layout.addWidget(self.tab_widget)
        # Bottom layout 
        bottom_layout = QHBoxLayout()
        self.borrow_button = QPushButton("Borrow")
        self.return_button = QPushButton("Return")
        self.edit_profile_button = QPushButton("Edit Profile")
        bottom_layout.addWidget(self.borrow_button)
        bottom_layout.addWidget(self.return_button)
        bottom_layout.addWidget(self.edit_profile_button)
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

    def borrow_book(self):
        # Get the selected row
        selected_row = self.catalog_table.currentRow()
        number_of_selected_rows = len(self.catalog_table.selectionModel().selectedRows())
        if number_of_selected_rows == 1:
            # Get book information from the selected row
            title = self.catalog_table.item(selected_row, 0).text()
            author = self.catalog_table.item(selected_row, 1).text()
            # Find the user in the database
            user_id = GlobalState.current_user
            users_collection = self.database_manager.db["users"]
            user_query = {"_id": user_id}
            user_document = users_collection.find_one(user_query)
            # Find the _id of the book based on title and author
            books_collection = self.database_manager.db["books"]
            book_query = {"title": title, "author": author}
            book_document = books_collection.find_one(book_query)
            if not user_document:
                QMessageBox.warning(self, "Borrow Failed", f"User not found in the database.")
                return
            if not book_document:
                QMessageBox.warning(self, "Borrow Failed", f"Book not found in the database.")
                return
            else:
                book_id = book_document["_id"]
            # Check if there are items available for borrowing
            items = self.get_available_items(books_collection, book_id)
            if items <= 0:
                QMessageBox.warning(self, "Borrow Failed", f"The book '{title}' by {author} is out of stock.")
                return
            # Check if the user has reached the maximum limit of borrowed books (6 books)
            elif self.is_max_books_borrowed(user_id):
                QMessageBox.warning(self, "Book Limit Exceeded", "You have already borrowed the maximum allowed number of books (6).")
                return
            # Check if the book is already in the user's borrowed_books
            elif self.is_book_already_borrowed(user_id, book_id):
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
                    self.borrow_selected_book(user_id, book_id, title, author, books_collection)
        else:
            return

    def borrow_selected_book(self, user_id, book_id, title, author, books_collection):
            # Insert a document into the 'borrowed_books' collection
            borrowed_books_collection = self.database_manager.db["borrowed_books"]
            borrow_date = datetime.utcnow()
            expiry_date = borrow_date + timedelta(minutes=15) 
            borrowed_book = {
                "user_id": user_id,
                "book_id": book_id,
                "borrow_date": borrow_date,
                "expiry_date": expiry_date
            }
            borrowed_books_collection.insert_one(borrowed_book)
            # Update the 'items' field in the 'books' collection (decrement by 1)
            update_query = {"$inc": {"items": -1}}
            books_collection.update_one({"_id": book_id}, update_query)
            self.statusBar.showMessage(f"You have borrowed '{title}' by {author}.", 8000)
            # Add the book to the user's history
            self.add_to_user_history(user_id, book_id, borrow_date)
            self.display_borrowed_books()

    def get_available_items(self, books_collection, book_id):
        book = books_collection.find_one({"_id": book_id})
        if book:
            return book.get("items", 0)  
        else:
            return 0  

    def is_book_already_borrowed(self, user_id, book_id):
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        existing_borrowed_book = borrowed_books_collection.find_one(
            {"user_id": user_id, "book_id": book_id}
        )
        return existing_borrowed_book is not None

    def is_max_books_borrowed(self, user_id):
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        borrowed_books_count = borrowed_books_collection.count_documents(
            {"user_id": user_id}
        )
        return borrowed_books_count >= 6

    def display_borrowed_books(self):
        display_borrowed_books(self, GlobalState.current_user, self.borrowed_books_table)

    def add_to_user_history(self, user_id, book_id, borrow_date):
        # Add the book information into the user's history
        history_collection = self.database_manager.db["customer_history"]
        history_entry = {
            "user_id": user_id,
            "book_id": book_id,
            "borrow_date": borrow_date,
        }
        history_collection.insert_one(history_entry)
        self.display_history()

    def display_history(self):
        display_book_history(self, self.history_table)

    def return_book(self):
        selected_row = self.tab_widget.widget(1).layout().itemAt(0).widget().currentRow()
        number_of_selected_rows = len(self.tab_widget.widget(1).layout().itemAt(0).widget().selectionModel().selectedRows())
        if number_of_selected_rows == 1:
            # Get book information from the selected row
            title = self.tab_widget.widget(1).layout().itemAt(0).widget().item(selected_row, 0).text()
            author = self.tab_widget.widget(1).layout().itemAt(0).widget().item(selected_row, 1).text()
            # Find the user in the database
            user_id = GlobalState.current_user
            users_collection = self.database_manager.db["users"]
            user_query = {"_id": user_id}
            user_document = users_collection.find_one(user_query)
            # Find the _id of the book based on title and author
            books_collection = self.database_manager.db["books"]
            book_query = {"title": title, "author": author}
            book_document = books_collection.find_one(book_query)
 
            if not user_document:
                QMessageBox.warning(self, "Return Failed", f"User not found in the database.")
                return
            # Get the book id
            book_id = book_document["_id"]
            # Confirm returning with the user
            reply = QMessageBox.question(
                self,
                "Return Book",
                f"Do you want to return '{title}' by {author}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.return_selected_book(user_id, book_id, title, author)
        else:
            return

    def return_selected_book(self, user_id, book_id, title, author):
        # Increasing the number of copies in the 'books' database is done via MongoDB Triggers.
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        return_query = {"user_id": user_id, "book_id": book_id}
        borrowed_books_collection.delete_one(return_query)
        self.statusBar.showMessage(f"You have returned '{title}' by {author}.", 8000)
        self.display_borrowed_books()
        # Not refreshing the book catalog because of possible applied filters

    def search_books(self):
        advanced_search(self, self.signals, self.statusBar, self.catalog_table, self.refresh_catalog_button, self.cancel_button)

    def sort_books(self):
        sort_book_catalog(self, self.signals, self.catalog_table, self.refresh_catalog_button, self.cancel_button)
      
    def cancel_search_or_sort(self):
        self.refresh_catalog_button.setEnabled(True)
        self.cancel_button.setEnabled(False) 
        self.signals.update_status_bar_widget.emit("")
        self.display_books()

    def edit_details(self):
        user_collection = self.database_manager.db["users"]
        query = {"_id": GlobalState.current_user}
        user_data = user_collection.find_one(query)
        # Check if the user has already tried to change the details
        edited_accounts_collection = self.database_manager.db["edited_accounts"]
        is_there_record = edited_accounts_collection.find_one(query)
        if is_there_record:
            QMessageBox.information(self, "Change of Details Failed", "Wait for the librarian to process the previous request to change the information.")
            return
        # Check if the user exists in the database(hasn't been banned/deleted)
        if user_data:
            dialog = EditProfileDialog(user_data, "Customer")
            result = dialog.exec()
            # If accept button was pressed
            if result == QDialog.DialogCode.Accepted:
                username_text = dialog.username_input.text()
                password_text = dialog.password_input.text()
                first_name_text = dialog.first_name_input.text()
                last_name_text = dialog.last_name_input.text()
                ssn_text = dialog.ssn_input.text()
                address_text = dialog.address_input.text()
                # Check if any information has been changed
                if (
                    username_text == user_data["username"] and
                    password_text == "" and
                    first_name_text == user_data["first_name"] and
                    last_name_text == user_data["last_name"] and
                    ssn_text == user_data["ssn"] and
                    address_text == user_data["address"]
                ):
                    QMessageBox.information(self, "No Changes", "No information has been changed.")
                    return
                # If the password field was empty
                password = (
                    user_data["password"] if password_text == "" else
                    str(bcrypt.hashpw(password_text.encode('utf-8'), bcrypt.gensalt()), 'utf-8')
                )
                # Check if all fields are filled in
                if any(not field for field in [username_text, password, first_name_text, last_name_text, ssn_text, address_text]):
                    QMessageBox.information(self, "Incomplete Information", "All fields except 'Password' must be filled in.")
                    return
                # Check if SSN is 10 characters long
                if not len(ssn_text) == 10:
                    QMessageBox.information(self, "Account Changes Failed", "The SSN must be 10 characters long (no slash)")
                    return
                # Check if the username or SSN already exists in the database
                inactivated_accounts_collection = self.database_manager.db["inactivated_accounts"]
                customer_collection = self.database_manager.db["users"]
                banned_accounts_collection = self.database_manager.db["banned_accounts"]
                # Exclude the current user from the query
                existing_username_query = {"username": username_text, "_id": {"$ne": GlobalState.current_user}}
                existing_ssn_query = {"ssn": ssn_text, "_id": {"$ne": GlobalState.current_user}}
                existing_username = customer_collection.find_one(existing_username_query)
                existing_ssn = customer_collection.find_one(existing_ssn_query)
                existing_inactivated_username = inactivated_accounts_collection.find_one({"username": username_text, "_id": {"$ne": GlobalState.current_user}})
                existing_inactivated_ssn = inactivated_accounts_collection.find_one({"ssn": ssn_text, "_id": {"$ne": GlobalState.current_user}})
                existing_banned_username = banned_accounts_collection.find_one({"username": username_text, "_id": {"$ne": GlobalState.current_user}})
                existing_banned_ssn = banned_accounts_collection.find_one({"ssn": ssn_text, "_id": {"$ne": GlobalState.current_user}})
                if (existing_username and existing_ssn) or (existing_inactivated_username and existing_inactivated_ssn) or (existing_banned_username and existing_banned_ssn):
                    QMessageBox.information(self, "Registration Failed", "Username and birth number already exist.")
                elif existing_username or existing_inactivated_username or existing_banned_username:
                    QMessageBox.information(self, "Registration Failed", "Username already exists.")
                elif existing_ssn or existing_inactivated_ssn or existing_banned_ssn:
                    QMessageBox.information(self, "Registration Failed", "Birth number already exists.")
                else:
                    edited_data = {
                        "_id" : GlobalState.current_user,
                        "username": username_text,
                        "password": password,
                        "first_name": first_name_text,
                        "last_name": last_name_text,
                        "ssn": ssn_text,
                        "address": address_text,
                    }
                    self.statusBar.showMessage(f"The changes have been sent to the librarian for approval.", 8000)
                    edited_accounts_collection.insert_one(edited_data)
            else:
                QMessageBox.information(self, "Change of Details Cancelled", "No changes have been made.")
        else:
            QMessageBox.warning(self, "Account Changes Failed", "User not found in the database.")
