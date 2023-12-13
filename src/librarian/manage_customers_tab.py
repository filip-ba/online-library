from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QListWidget, QListWidgetItem, QScrollArea,  
      QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QDialog, QGroupBox, QHeaderView, QAbstractItemView )
from PyQt6.QtCore import Qt
from database_manager import DatabaseManager
from dialogs.registration_dialog import RegistrationDialog
from dialogs.edit_profile_dialog import EditProfileDialog
from dialogs.sort_dialog import SortDialog
from dialogs.search_dialog import SearchDialog
from shared_functions import create_account
from shared_functions import display_borrowed_books


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
        self.refresh_button.clicked.connect(lambda: self.display_customers())
        self.refresh_button.clicked.connect(self.display_banned_accounts)
        self.refresh_button.clicked.connect(self.display_inactivated_accounts)
        self.refresh_button.clicked.connect(self.display_edited_accounts)
        self.confirm_account_button.clicked.connect(self.accept_activation)
        self.decline_account_button.clicked.connect(self.decline_activation)
        self.confirm_changes_button.clicked.connect(self.accept_account_changes)
        self.decline_changes_button.clicked.connect(self.decline_account_changes)
        self.add_account_button.clicked.connect(self.register_user)
        self.edit_account_button.clicked.connect(self.edit_customer_account)
        self.ban_account_button.clicked.connect(self.ban_account)
        self.unban_account_button.clicked.connect(self.unban_account)
        self.sort_button.clicked.connect(self.sort_customers)
        self.search_button.clicked.connect(self.search_customers)
        self.cancel_button.clicked.connect(self.cancel_search_or_sort)
        self.show_borrowed_button.clicked.connect(self.display_borrowed_books)

    def init_librarian_tab(self):
        self.display_customers()
        self.display_banned_accounts()
        self.display_inactivated_accounts()
        self.display_edited_accounts()
        self.pending_accounts_message()
        self.tab_widget.setCurrentIndex(0)
        self.cancel_button.setEnabled(False)
        self.refresh_button.setEnabled(True)

    def pending_accounts_message(self):
        inactivated_accounts_collection = self.database_manager.db["inactivated_accounts"]
        pending_accounts_count = inactivated_accounts_collection.count_documents({})
        if pending_accounts_count > 0:
            self.statusBar.showMessage(f"There are {pending_accounts_count} accounts waiting for activation.", 8000)

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
        self.refresh_button = QPushButton("Refresh Lists")
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
        books_actions_layout.addWidget(self.show_borrowed_button)
        books_actions_layout.addWidget(self.show_history_button)
        books_actions_layout.addWidget(self.assign_book_button)
        # GroupBox for Add Account, Edit Account, Ban Account, Unban Account
        group_box_4 = QGroupBox("Account Actions")
        account_actions_layout = QVBoxLayout(group_box_4)
        self.add_account_button = QPushButton("Add Account")
        self.edit_account_button = QPushButton("Edit Account")
        self.ban_account_button = QPushButton("Ban Account")
        self.unban_account_button = QPushButton("Unban Account")
        account_actions_layout.addWidget(self.add_account_button)
        account_actions_layout.addWidget(self.edit_account_button)
        account_actions_layout.addWidget(self.ban_account_button)
        account_actions_layout.addWidget(self.unban_account_button)
        # QTableWidget for Customer Accounts
        self.tab_widget = QTabWidget()
        self.tab_widget.setMinimumWidth(375)
        self.customers_table = QTableWidget()
        customer_table_tab = QWidget()
        self.customers_table.setColumnCount(5) 
        self.customers_table.setHorizontalHeaderLabels(["Username", "First Name", "Last Name", "SSN", "Address"])
        self.customers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header = self.customers_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        customer_table_layout = QVBoxLayout(customer_table_tab)
        customer_table_layout.addWidget(self.customers_table)
        self.tab_widget.addTab(customer_table_tab, "Customer Table")
        # QTableWidget for Banned Accounts
        self.banned_accounts_table = QTableWidget()
        banned_accounts_tab = QWidget()
        self.banned_accounts_table.setColumnCount(5)
        self.banned_accounts_table.setHorizontalHeaderLabels(["Username", "First Name", "Last Name", "SSN", "Address"])
        self.banned_accounts_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        header_2 = self.banned_accounts_table.horizontalHeader()
        header_2.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        banned_accounts_layout = QVBoxLayout(banned_accounts_tab)
        banned_accounts_layout.addWidget(self.banned_accounts_table)
        self.tab_widget.addTab(banned_accounts_tab, "Banned Accounts")
        # List Widget for Account Activation
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
        # List Widget for Account Changes Confirmation
        list_layout_2 = QVBoxLayout()
        button_layout_2 = QHBoxLayout()
        self.list_widget_confirm_changes = QListWidget()
        list_title__2 = QLabel("Confirm Account Changes")
        self.confirm_changes_button = QPushButton("Confirm")
        self.decline_changes_button = QPushButton("Decline")
        button_layout_2.addWidget(self.confirm_changes_button)
        button_layout_2.addWidget(self.decline_changes_button)
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
        left_layout.addWidget(group_box_3)
        left_layout.addWidget(group_box_4)
        left_layout.addWidget(group_box_2)
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

    def display_customers(self, cursor=None):
        if cursor is None:
            users_collection = self.database_manager.db["users"]
            cursor = users_collection.find()
        self.customers_table.setRowCount(0)
        self.customers_table.setWordWrap(True) 
        for index, customer in enumerate(cursor):
            self.customers_table.insertRow(index)
            for col, prop in enumerate(["username", "first_name", "last_name", "ssn", "address"]):
                item = QTableWidgetItem(str(customer[prop]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) 
                self.customers_table.setItem(index, col, item)
            self.customers_table.setRowHeight(index, 50)
        self.customers_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def display_borrowed_books(self):
        selected_row = self.customers_table.currentRow()
        number_of_selected_rows = len(self.customers_table.selectionModel().selectedRows())
        if number_of_selected_rows != 1:
            return
        account_username = self.customers_table.item(selected_row, 0).text()
        user_collection = self.database_manager.db["users"]
        query = {"username": account_username}
        user_data = user_collection.find_one(query)
        # If the user exists, open the dialog
        if user_data:
            user_id = user_data["_id"]
            self.borrowed_books_dialog(user_id, account_username)
        else:
            QMessageBox.warning(self, "Account Changes Failed", "User not found in the database.")

    def borrowed_books_dialog(self, user_id, account_username):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"{account_username}'s borrowed books")
        dialog.setFixedSize(800, 700)
        layout = QVBoxLayout(dialog)
        table_widget = QTableWidget(dialog)
        table_widget.setColumnCount(7)
        table_widget.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Book Cover", "Borrow Date", "Due Date"])
        table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        horizontal_header = table_widget.horizontalHeader()
        horizontal_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Populate the table with the user's borrowed books
        display_borrowed_books(self, user_id, table_widget)
        if table_widget.rowCount() >= 5:
            vertical_header = table_widget.verticalHeader()
            vertical_header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Buttons
        button_layout = QHBoxLayout()
        remove_button = QPushButton("Remove the Book", dialog)
        remove_button.clicked.connect(lambda: self.return_selected_book(table_widget, user_id, account_username))
        cancel_button = QPushButton("Cancel", dialog)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(cancel_button)
        # Add widgets to the layout
        layout.addWidget(table_widget)
        layout.addLayout(button_layout)
        dialog.exec()

    def return_selected_book(self, table_widget, user_id, account_username):
        selected_row = table_widget.currentRow()
        number_of_selected_rows = len(table_widget.selectionModel().selectedRows())
        if number_of_selected_rows != 1:
            return
        title = table_widget.item(selected_row, 0).text()
        author = table_widget.item(selected_row, 1).text()
        books_collection = self.database_manager.db["books"]
        book_query = {"title": title, "author": author}
        book_document = books_collection.find_one(book_query)
        book_id = book_document["_id"]
        if book_id:
            reply = QMessageBox.question(
                self,
                "Return Book",
                f"Do you want to return '{title}' by {author}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel
            )
            if reply == QMessageBox.StandardButton.Yes:
                borrowed_books_collection = self.database_manager.db["borrowed_books"]
                delete_query = {"user_id": user_id, "book_id": book_id}
                # Delete the book from the borrowed_books collection
                borrowed_books_collection.delete_one(delete_query)
                # Remove the book from the table
                table_widget.removeRow(selected_row)
                # Display a message
                QMessageBox.information(self, "Book Returned", f"The book has been returned.")
                self.statusBar.showMessage(f"The book '{title}' has been removed from the user '{account_username}'.", 8000)
        else:
            QMessageBox.warning(self, "Return Failed", f"Book not found in the database.")

    def display_banned_accounts(self):
        banned_accounts_collection = self.database_manager.db["banned_accounts"]
        banned_accounts_data = banned_accounts_collection.find()
        self.banned_accounts_table.setRowCount(0)
        self.customers_table.setWordWrap(True) 
        for index, customer in enumerate(banned_accounts_data):
            self.banned_accounts_table.insertRow(index)
            for col, prop in enumerate(["username", "first_name", "last_name", "ssn", "address"]):
                item = QTableWidgetItem(str(customer[prop]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter) 
                self.banned_accounts_table.setItem(index, col, item)
            self.banned_accounts_table.setRowHeight(index, 50)
        self.banned_accounts_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def display_inactivated_accounts(self):
        inactivated_accounts_collection = self.database_manager.db["inactivated_accounts"]
        inactivated_accounts_data = inactivated_accounts_collection.find()
        self.list_widget_activate_acc.clear()
        for account_data in inactivated_accounts_data:
            username = account_data.get("username")
            first_name = account_data.get("first_name")
            last_name = account_data.get("last_name")
            ssn = account_data.get("ssn")
            address = account_data.get("address")
            user = (f"User '{username}', First Name '{first_name}', Last Name '{last_name}', SSN '{ssn}', Address '{address}'")
            list_item = QListWidgetItem(user)
            list_item.setData(Qt.ItemDataRole.UserRole, account_data.get("_id"))
            self.list_widget_activate_acc.addItem(list_item)

    def display_edited_accounts(self):
        edited_accounts_collection = self.database_manager.db["edited_accounts"]
        edited_accounts_data = edited_accounts_collection.find()
        self.list_widget_confirm_changes.clear()
        for account_data in edited_accounts_data:
            username = account_data.get("username")
            first_name = account_data.get("first_name")
            last_name = account_data.get("last_name")
            ssn = account_data.get("ssn")
            address = account_data.get("address")
            user = (f"User '{username}', First Name '{first_name}', Last Name '{last_name}', SSN '{ssn}', Address '{address}'")
            list_item = QListWidgetItem(user)
            list_item.setData(Qt.ItemDataRole.UserRole, account_data.get("_id"))
            self.list_widget_confirm_changes.addItem(list_item)

    def register_user(self):
        dialog = RegistrationDialog()
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            create_account(self, dialog.username_signup.text(), dialog.password_signup.text(), dialog.first_name_signup.text(), dialog.last_name_signup.text(), dialog.ssn_signup.text(), dialog.address_signup.text(), "Librarian", self.statusBar)
            self.display_customers()

    def accept_activation(self):
        selected_item = self.list_widget_activate_acc.currentItem()
        if selected_item:
            # Retrieve the associated user ID
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            # Fetch the user data from the inactivated accounts collection
            inactivated_accounts_collection = self.database_manager.db["inactivated_accounts"]
            account_data = inactivated_accounts_collection.find_one({"_id": user_id})
            confirm_message = "Are you sure you want to accept this account request?"
            confirm_result = QMessageBox.question(self, "Confirmation", confirm_message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm_result == QMessageBox.StandardButton.Yes:
                if account_data:
                    users_collection = self.database_manager.db["users"]
                    users_collection.insert_one({
                        "username": account_data.get("username"),
                        "password": account_data.get("password"),
                        "first_name": account_data.get("first_name"),
                        "last_name": account_data.get("last_name"),
                        "ssn": account_data.get("ssn"),
                        "address": account_data.get("address"),
                    })
                    # Remove the document from the inactivated accounts collection
                    inactivated_accounts_collection.delete_one({"_id": user_id})
                    # Refresh the displayed inactivated accounts and customers
                    self.display_inactivated_accounts()
                    self.display_customers()
                    self.statusBar.showMessage(f"The account '{account_data["username"]}' has been activated.", 8000)
                else:
                    QMessageBox.warning(self, "Error", "Unable to find account data.")
        
    def decline_activation(self):
        selected_item = self.list_widget_activate_acc.currentItem()
        if selected_item:
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            confirm_message = "Are you sure you want to decline this account request?"
            confirm_result = QMessageBox.question(self, "Confirmation", confirm_message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm_result == QMessageBox.StandardButton.Yes:
                inactivated_accounts_collection = self.database_manager.db["inactivated_accounts"]
                inactivated_accounts_collection.delete_one({"_id": user_id})
                self.display_inactivated_accounts()
                self.statusBar.showMessage(f"The account request has been declined.", 8000)

    def accept_account_changes(self):
        selected_item = self.list_widget_confirm_changes.currentItem()
        if selected_item:
            # Retrieve the associated user ID
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            # Fetch the user data from the inactivated accounts collection
            edited_accounts_collection = self.database_manager.db["edited_accounts"]
            account_data = edited_accounts_collection.find_one({"_id": user_id})
            confirm_message = "Are you sure you want to accept this change request?"
            confirm_result = QMessageBox.question(self, "Confirmation", confirm_message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm_result == QMessageBox.StandardButton.Yes:
                if account_data:
                    users_collection = self.database_manager.db["users"]
                    query = {
                        "$set": {
                            "username": account_data.get("username"),
                            "password": account_data.get("password"),
                            "first_name": account_data.get("first_name"),
                            "last_name": account_data.get("last_name"),
                            "ssn": account_data.get("ssn"),
                            "address": account_data.get("address"),
                        }
                    }
                    # Update the user data in the users collection
                    users_collection.update_one({"_id": user_id}, query)
                    # Delete the record from the edited_accounts collection
                    edited_accounts_collection.delete_one({"_id": user_id})
                    self.display_edited_accounts()
                    self.display_customers()
                    self.statusBar.showMessage(f"The account changes have been accepted.", 8000)
                else:
                    QMessageBox.warning(self, "Error", "Unable to find account data.")

    def decline_account_changes(self):
        selected_item = self.list_widget_confirm_changes.currentItem()
        if selected_item:
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            users_db = self.database_manager.db["users"]
            does_user_exist = users_db.find_one({"_id": user_id})
            if does_user_exist:
                confirm_message = "Are you sure you want to decline this account edit request?"
                confirm_result = QMessageBox.question(self, "Confirmation", confirm_message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if confirm_result == QMessageBox.StandardButton.Yes:
                    edited_accounts_collection = self.database_manager.db["edited_accounts"]
                    edited_accounts_collection.delete_one({"_id": user_id})
                    self.display_edited_accounts()
                    self.statusBar.showMessage(f"The account changes has been declined.", 8000)
            else:
                QMessageBox.warning(self, "User Not Found", "The selected user was not found.")
            
    def edit_customer_account(self):
        selected_row = self.customers_table.currentRow()
        number_of_selected_rows = len(self.customers_table.selectionModel().selectedRows())
        if number_of_selected_rows != 1:
            return
        account_username = self.customers_table.item(selected_row, 0).text()
        user_collection = self.database_manager.db["users"]
        query = {"username": account_username}
        user_data = user_collection.find_one(query)
        # Check if the user exists in the database (hasn't been banned/deleted)
        if user_data:
            dialog = EditProfileDialog(user_data, "Librarian")  
            result = dialog.exec()
            # If accept button was pressed
            if result == QDialog.DialogCode.Accepted:
                user_id = user_data["_id"]
                username_text = dialog.username_input.text()
                first_name_text = dialog.first_name_input.text()
                last_name_text = dialog.last_name_input.text()
                ssn_text = dialog.ssn_input.text()
                address_text = dialog.address_input.text()
                # Check if any information has been changed
                if (
                    username_text == user_data["username"] and
                    first_name_text == user_data["first_name"] and
                    last_name_text == user_data["last_name"] and
                    ssn_text == user_data["ssn"] and
                    address_text == user_data["address"]
                ):
                    QMessageBox.information(self, "No Changes", "No information has been changed.")
                    return
                # If the password field was empty
                password = user_data["password"]
                # Check if all fields are filled in
                if any(not field for field in [username_text, password, first_name_text, last_name_text, ssn_text, address_text]):
                    QMessageBox.information(self, "Incomplete Information", "All fields must be filled in.")
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
                existing_username_query = {"username": username_text, "_id": {"$ne": user_id}}
                existing_ssn_query = {"ssn": ssn_text, "_id": {"$ne": user_id}}
                existing_username = customer_collection.find_one(existing_username_query)
                existing_ssn = customer_collection.find_one(existing_ssn_query)
                existing_inactivated_username = inactivated_accounts_collection.find_one({"username": username_text, "_id": {"$ne": user_id}})
                existing_inactivated_ssn = inactivated_accounts_collection.find_one({"ssn": ssn_text, "_id": {"$ne": user_id}})
                existing_banned_username = banned_accounts_collection.find_one({"username": username_text, "_id": {"$ne": user_id}})
                existing_banned_ssn = banned_accounts_collection.find_one({"ssn": ssn_text, "_id": {"$ne": user_id}})
                if (existing_username and existing_ssn) or (existing_inactivated_username and existing_inactivated_ssn) or (existing_banned_username and existing_banned_ssn):
                    QMessageBox.information(self, "Registration Failed", "Username and birth number already exist.")
                elif existing_username or existing_inactivated_username or existing_banned_username:
                    QMessageBox.information(self, "Registration Failed", "Username already exists.")
                elif existing_ssn or existing_inactivated_ssn or existing_banned_ssn:
                    QMessageBox.information(self, "Registration Failed", "Birth number already exists.")
                else:
                    # Update the document in the users collection
                    updated_data = {
                        "username": username_text,
                        "password": password,
                        "first_name": first_name_text,
                        "last_name": last_name_text,
                        "ssn": ssn_text,
                        "address": address_text,
                    }
                    user_collection.update_one({"_id": user_id}, {"$set": updated_data})
                    self.display_customers()
                    self.statusBar.showMessage(f"The changes for {username_text}'s account have been applied.", 8000)
            else:
                QMessageBox.information(self, "Change of Details Cancelled", "No changes have been made.")
        else:
            QMessageBox.warning(self, "Account Changes Failed", "User not found in the database.")

    def ban_account(self):
        selected_row = self.customers_table.currentRow()
        number_of_selected_rows = len(self.customers_table.selectionModel().selectedRows())
        if number_of_selected_rows != 1:
            return
        account_username = self.customers_table.item(selected_row, 0).text()
        user_collection = self.database_manager.db["users"]
        query = {"username": account_username}
        user_data = user_collection.find_one(query)
        user_id = user_data["_id"]
        banned_accounts_collection = self.database_manager.db["banned_accounts"]
        # Check if the user exists in the database (hasn't been banned/deleted)
        if user_data:
            confirm_message = f"Are you sure you want to ban the account of '{user_data["username"]}'?"
            confirm_result = QMessageBox.question(self, "Confirmation", confirm_message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm_result == QMessageBox.StandardButton.Yes:
                # Copy the user data to banned_accounts collection
                banned_accounts_collection.insert_one(user_data)
                # Remove the user data from the users collection
                user_collection.delete_one({"_id": user_id})
                self.statusBar.showMessage(f"The account of {user_data['username']} has been banned.", 8000)
                self.display_customers()
                self.display_banned_accounts()
        else:
            QMessageBox.warning(self, "Ban Account Failed", "User not found in the database.")

    def unban_account(self):
        selected_row = self.banned_accounts_table.currentRow()
        number_of_selected_rows = len(self.banned_accounts_table.selectionModel().selectedRows())
        if number_of_selected_rows != 1:
            return
        account_username = self.banned_accounts_table.item(selected_row, 0).text()
        banned_accounts_collection = self.database_manager.db["banned_accounts"]
        query = {"username": account_username}
        user_data = banned_accounts_collection.find_one(query)
        user_id = user_data["_id"]
        user_collection = self.database_manager.db["users"]
        # Check if the user exists in the database (hasn't been banned/deleted)
        if user_data:
            confirm_message = f"Are you sure you want to unban the account of '{user_data['username']}'?"
            confirm_result = QMessageBox.question(self, "Confirmation", confirm_message, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if confirm_result == QMessageBox.StandardButton.Yes:
                # Copy the user data back to users collection
                user_collection.insert_one(user_data)
                # Remove the user data from banned_accounts collection
                banned_accounts_collection.delete_one({"_id": user_id})
                self.statusBar.showMessage(f"The account of {user_data['username']} has been unbanned.", 8000)
                # Refresh the tables
                self.display_customers()
                self.display_banned_accounts()
        else:
            QMessageBox.warning(self, "Unban Account Failed", "User not found in the banned accounts collection.")
            
    def sort_customers(self):
        combo_box_items = ["First Name", "Last Name", "Address" ,"Birth Number"]
        dialog = SortDialog(combo_box_items)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            combo_box_input = dialog.attribute_combo.currentText().lower()
            if combo_box_input == "first name":
                sort_attr = "first_name"
            elif combo_box_input == "last name":
                sort_attr = "last_name"
            elif combo_box_input == "birth number":
                sort_attr = "ssn"
            elif combo_box_input == "address":
                sort_attr = "address"
            sort_ascend =  dialog.ascending_radio.isChecked()
            self.refresh_button.setEnabled(False) 
            self.cancel_button.setEnabled(True)
            users_collection = self.database_manager.db["users"]
            cursor = users_collection.find().sort([(sort_attr, 1 if sort_ascend == True else -1)])
            self.signals.update_status_bar_widget_2.emit(f"Customers sorted by {combo_box_input}")
            self.display_customers(cursor)

    def search_customers(self):
        role = "Librarian"
        label_1 = "First Name:"
        label_2 = "Last Name:"
        label_3 = "SSN:"
        label_4 = "Address:"
        dialog = SearchDialog(role, label_1, label_2, label_3, label_4)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            first_name_text = dialog.input_1.text()
            last_name_text = dialog.input_2.text()
            ssn_text = dialog.input_3.text()
            address_text = dialog.input_4.text()
            users_collection = self.database_manager.db["users"]
            first_name_formatted = ""
            last_name_formatted = ""
            ssn_formatted = ""
            address_formatted = ""
            query = {}
            if len(first_name_text) >= 3:
                query["first_name"] = {"$regex": first_name_text, "$options": "i"}
                first_name_formatted =(f"  First Name: '{first_name_text}'")
            if len(last_name_text) >= 3:
                query["last_name"] = {"$regex": last_name_text, "$options": "i"}
                last_name_formatted =(f"  Last Name: '{last_name_text}'")
            if len(ssn_text) >= 3:
                query["ssn"] = {"$regex": ssn_text, "$options": "i"}
                ssn_formatted =(f"  SSN: '{ssn_text}'")
            if len(address_text) >= 3:
                query["address"] = {"$regex": address_text, "$options": "i"}
                address_formatted =(f"  Address: '{address_text}'")
            if len(first_name_text) >= 3 or len(last_name_text) >= 3 or len(ssn_text)>= 3 or len(address_text):
                self.signals.update_status_bar_widget_2.emit(f"Showing customer searches for: {first_name_formatted}{last_name_formatted}{ssn_formatted}{address_formatted}")
                self.refresh_button.setEnabled(False)   # Disabling the button to refresh search results
                self.cancel_button.setEnabled(True)    # Disable the button to cancel the search if the search is not in progress
                cursor = users_collection.find(query)
                self.display_customers(cursor)
            else:
                self.statusBar.showMessage("The minimum character length required for searching is 3.", 8000)
                return 

    def cancel_search_or_sort(self):
        self.refresh_button.setEnabled(True)
        self.cancel_button.setEnabled(False) 
        self.signals.update_status_bar_widget_2.emit("")
        self.display_customers()

        


