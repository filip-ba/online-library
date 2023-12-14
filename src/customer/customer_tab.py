from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QDialog,
      QHBoxLayout, QTableWidget, QHeaderView, QAbstractItemView, QTableWidgetItem )
import bcrypt  
from database_manager import DatabaseManager
from global_state import GlobalState
from shared_functions import display_book_catalog
from shared_functions import display_borrowed_books
from shared_functions import display_book_history
from shared_functions import search_book_catalog
from shared_functions import sort_book_catalog
from shared_functions import borrow_book
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
        self.borrow_button.clicked.connect(self.borrow_selected_book)
        self.return_button.clicked.connect(self.return_book)
        self.edit_profile_button.clicked.connect(self.edit_details)
        self.delete_history_button.clicked.connect(self.delete_history)

    def init_customer_tab(self):
        # Load the tables
        self.display_books()    
        self.display_borrowed_books()
        self.display_history()
        # Set the current tab of the tab widget to "book catalog"
        self.tab_widget.setCurrentIndex(0)
        # Set the default value at the beginning, because the state(enabled/disabled) of these 2 buttons can change
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
        self.delete_history_button = QPushButton("Delete History")
        bottom_layout.addWidget(self.borrow_button)
        bottom_layout.addWidget(self.return_button)
        bottom_layout.addWidget(self.edit_profile_button)
        bottom_layout.addWidget(self.delete_history_button)
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

    def borrow_selected_book(self):
        result = borrow_book(self, self.catalog_table, GlobalState.current_user, self.database_manager, self.statusBar, "Customer")
        # Refresh the tables of borrowed books and history if the book has been successfully borrowed
        if result == True:
            self.display_borrowed_books()
            self.display_history()

    def display_borrowed_books(self):
        display_borrowed_books(self, GlobalState.current_user, self.borrowed_books_table)

    def display_history(self):
        display_book_history(self, GlobalState.current_user, self.history_table)

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
            book_id = book_document["_id"]
            reply = QMessageBox.question(
                self, "Return Book", f"Do you want to return '{title}' by {author}?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel )
            if reply == QMessageBox.StandardButton.Yes:
                self.return_selected_book(user_id, book_id, title, author, selected_row)
        else:
            return

    def return_selected_book(self, user_id, book_id, title, author, selected_row):
        # Increase of the number of copies in the "books" collection is done via MongoDB Triggers
        borrowed_books_collection = self.database_manager.db["borrowed_books"]
        return_query = {"user_id": user_id, "book_id": book_id}
        borrowed_books_collection.delete_one(return_query)
        # Increment the number of items in the books collection
        position = self.find_book_position(title)
        if position != -1:
            updated_items = self.catalog_table.item(position, 4).text()
            updated_items = str(int(updated_items) + 1)  
            self.catalog_table.setItem(position, 4, QTableWidgetItem(updated_items))
        self.statusBar.showMessage(f"You have returned '{title}' by {author}.", 8000)
        self.borrowed_books_table.removeRow(selected_row)

    def find_book_position(self, title):
        for row in range(self.catalog_table.rowCount()):
            item = self.catalog_table.item(row, 0)
            if item and item.text() == str(title):
                return row  # Return the row index where the book is found
        return -1  # Return -1 if the book is not found in the table

    def delete_history(self):
        user_id = GlobalState.current_user
        users_collection = self.database_manager.db["users"]
        user_query = {"_id": user_id}
        user_document = users_collection.find_one(user_query)
        if not user_document:
            QMessageBox.warning(self, "History Deletion Failed", f"User not found in the database.")
            return
        confirm_result = QMessageBox.question(
            self, "Confirmation", "Are you sure you want to delete the borrowing history?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel )
        if confirm_result == QMessageBox.StandardButton.Yes:
            customer_history_collection = self.database_manager.db["customer_history"]
            deleted_count = customer_history_collection.delete_many({"user_id": user_id})
            if deleted_count.deleted_count > 0:
                self.display_history()
                self.statusBar.showMessage("History has been deleted.", 8000)
            else:
                QMessageBox.information(self, "No History Found", "No borrowing history found for clearing.")

    def search_books(self):
        search_book_catalog(self, self.signals, self.statusBar, self.catalog_table, self.refresh_catalog_button, self.cancel_button)

    def sort_books(self):
        sort_book_catalog(self, self.signals, self.catalog_table, self.refresh_catalog_button, self.cancel_button)
      
    def cancel_search_or_sort(self):
        self.refresh_catalog_button.setEnabled(True)    
        self.cancel_button.setEnabled(False)    
        self.signals.update_status_bar_widget.emit("")  # Clear the status bar widget
        self.display_books()    # Load the entire "books" collection 

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
                # Don't change the password if the password field was empty
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
                    # Insert the edited data into the edited_accounts collection
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
