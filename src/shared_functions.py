from PyQt6.QtWidgets import (QMessageBox, QTableWidget, QTableWidgetItem,
                             QLabel, QDialog )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from datetime import datetime
from pathlib import Path
import bcrypt  
import os
from global_state import GlobalState
from dialogs.advanced_search_dialog import AdvancedSearchDialog
from dialogs.sort_books_dialog import SortBooksDialog


def create_account(self, username, password, role, first_name, last_name, ssn, address, statusBar):
    # Check if anybody is logged in
    if not GlobalState.current_user == None:
        QMessageBox.information(self, "Registration Failed", "You must be logged out before registering.")
        return
    # Check if any required field is empty
    if any(not field for field in [username, password, role, first_name, last_name, ssn, address]):
        QMessageBox.information(self, "Registration Failed", "Please fill in all the required fields.")
        return
    # Check if the username or SSN already exists in the database
    customer_collection = self.database_manager.db["users"]
    existing_username = customer_collection.find_one({"username": username})
    existing_ssn = customer_collection.find_one({"ssn": ssn})
    if existing_username and existing_ssn:
        QMessageBox.information(self, "Registration Failed", "Username and birth number already exist.")
    elif existing_username:
        QMessageBox.information(self, "Registration Failed", "Username already exists.")
    elif existing_ssn:
        QMessageBox.information(self, "Registration Failed", "Birth number already exists.")
    else:
        # Save the new customer into the users collection
        new_customer = {
            "username": username,
            "password": str(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), 'utf-8'),  
            "role": role,
            "first_name": first_name,
            "last_name": last_name,
            "ssn": ssn,
            "address": address,
            "acc_activated": False,  
        }
        customer_collection.insert_one(new_customer)
        QMessageBox.information(self, "Customer registered", "Registration was successful. Waiting for approval.")
        # Show informational message in the status bar
        statusBar.showMessage(f"Registration successful. Waiting for librarian approval.", 5000)

def display_book_catalog(self, catalog_table, cursor=None):
    if cursor is None:
        books_collection = self.database_manager.db["books"]
        cursor = books_collection.find()
    catalog_table.setRowCount(0)
    for index, book in enumerate(cursor):
        catalog_table.insertRow(index)
        catalog_table.setItem(index, 0, QTableWidgetItem(book["title"]))
        catalog_table.setItem(index, 1, QTableWidgetItem(book["author"]))
        catalog_table.setItem(index, 2, QTableWidgetItem(str(book["pages"])))
        catalog_table.setItem(index, 3, QTableWidgetItem(str(book["year"])))
        catalog_table.setItem(index, 4, QTableWidgetItem(str(book["items"])))
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
            catalog_table.setRowHeight(index, scaled_pixmap.height())
            # Set the alignment of the image within the cell
            cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            catalog_table.setCellWidget(index, 5, cover_label)  
        else:
            placeholder_label = QLabel("No Image")
            catalog_table.setCellWidget(index, 5, placeholder_label) 
    # Set the whole table as read-only
    catalog_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

def display_book_history(self, history_table):
    # Display the user's book history in the history_table
    history_collection = self.database_manager.db["customer_history"]
    user_history = history_collection.find({"username": GlobalState.current_user})
    history_table.setRowCount(0)
    for index, history_entry in enumerate(user_history):
        history_table.insertRow(index)
        for col, prop in enumerate(["title", "author", "pages", "year"]):
            # Retrieve book information from the "books" collection
            books_collection = self.database_manager.db["books"]
            book_query = {"title": history_entry["title"], "author": history_entry["author"]}
            book = books_collection.find_one(book_query)
            history_table.setItem(index, col, QTableWidgetItem(str(book[prop])))
        # Display book cover image
        cover_label = QLabel()
        cover_path = os.path.join(Path(__file__).resolve().parent.parent, "book_covers", f"{book['image_name']}.png")
        if os.path.exists(cover_path):
            pixmap = QPixmap(cover_path)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            cover_label.setPixmap(scaled_pixmap)
            history_table.setRowHeight(index, scaled_pixmap.height())
            cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            history_table.setCellWidget(index, 4, cover_label)
        else:
            placeholder_label = QLabel("No Image")
            history_table.setCellWidget(index, 4, placeholder_label)
        # Display the event date in the fifth column
        formatted_event_date = datetime.strftime(history_entry["event_date"], "%d/%m/%Y, %H:%M")
        history_table.setItem(index, 5, QTableWidgetItem(formatted_event_date))
    history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

def advanced_search(self, signals, statusBar, catalog_table, refresh_catalog_button, cancel_button):
    dialog = AdvancedSearchDialog()
    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        author_text = dialog.author_input.text()
        title_text = dialog.title_input.text()
        year_text = dialog.year_input.text()
        books_collection = self.database_manager.db["books"]
        author_formatted = ""
        title_formatted = ""
        year_formatted = ""
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
            signals.update_status_bar_widget.emit(f"Showing searches for: {author_formatted}{title_formatted}{year_formatted}")
            refresh_catalog_button.setEnabled(False)   # Disabling the button to refresh search results
            cancel_button.setEnabled(True)    # Disable the button to cancel the search if the search is not in progress
            cursor = books_collection.find(query)
            display_book_catalog(self, catalog_table, cursor)
        else:
            statusBar.showMessage("The minimum character length required for searching is 3.", 7000)
            return 

def sort_book_catalog(self, signals, catalog_table, refresh_catalog_button, cancel_button):
    dialog = SortBooksDialog()
    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        sort_attr = dialog.attribute_combo.currentText().lower()
        sort_ascend =  dialog.ascending_radio.isChecked()
        refresh_catalog_button.setEnabled(False) 
        cancel_button.setEnabled(True)
        books_collection = self.database_manager.db["books"]
        cursor = books_collection.find().sort([(sort_attr, 1 if sort_ascend == True else -1)])
        signals.update_status_bar_widget.emit(f"Sorted by {sort_attr}")
        display_book_catalog(self, catalog_table, cursor)
