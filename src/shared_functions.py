from PyQt6.QtWidgets import (QMessageBox, QTableWidget, QTableWidgetItem,
                             QLabel, QDialog )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from datetime import datetime, timedelta
from pathlib import Path
import bcrypt  
import os
from global_state import GlobalState
from dialogs.search_dialog import SearchDialog
from dialogs.sort_dialog import SortDialog


def create_account(self, username, password, first_name, last_name, ssn, address, creator, statusBar):
    # Check if anybody is logged in
    if creator == "Customer" and not GlobalState.current_user == None:
        QMessageBox.information(self, "Registration Failed", "You must be logged out before registering.")
        return False
    # Check if any required field is empty
    if any(not field for field in [username, password, creator, first_name, last_name, ssn, address]):
        QMessageBox.information(self, "Registration Failed", "Please fill in all the required fields.")
        return False
    if not len(ssn) == 10:
        QMessageBox.information(self, "Registration Failed", "The SSN must be 10 characters long (no slash)")
        return False
    # Check if the username or SSN already exists in the database
    inactivated_accounts_collection = self.database_manager.db["inactivated_accounts"]
    customer_collection = self.database_manager.db["users"]
    banned_accounts_collection = self.database_manager.db["banned_accounts"]
    existing_username = customer_collection.find_one({"username": username})
    existing_ssn = customer_collection.find_one({"ssn": ssn})
    existing_inactivated_username = inactivated_accounts_collection.find_one({"username": username})
    existing_inactivated_ssn = inactivated_accounts_collection.find_one({"ssn": ssn})
    existing_banned_username = banned_accounts_collection.find_one({"username": username})
    existing_banned_ssn = banned_accounts_collection.find_one({"ssn": ssn})
    if (existing_username and existing_ssn) or (existing_inactivated_username and existing_inactivated_ssn) or (existing_banned_username and existing_banned_ssn):
        QMessageBox.information(self, "Registration Failed", "Username and birth number already exist.")
    elif existing_username or existing_inactivated_username or existing_banned_username:
        QMessageBox.information(self, "Registration Failed", "Username already exists.")
    elif existing_ssn or existing_inactivated_ssn or existing_banned_ssn:
        QMessageBox.information(self, "Registration Failed", "Birth number already exists.")
    else:
        new_customer = {
            "username": username,
            "password": str(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()), 'utf-8'),  
            "first_name": first_name,
            "last_name": last_name,
            "ssn": ssn,
            "address": address,
        }
        if creator == "Customer":
            inactivated_accounts_collection.insert_one(new_customer)
            QMessageBox.information(self, "Customer registered", "Registration was successful. Waiting for approval.")
            statusBar.showMessage(f"Registration successful. Waiting for librarian approval.", 8000)
            return True
        else:
            customer_collection.insert_one(new_customer)
            QMessageBox.information(self, "Customer registered", "Registration was successful.")
            statusBar.showMessage(f"Registration successful.", 8000)
            return False

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
        cover_path = os.path.join(Path(__file__).resolve().parent.parent, "book_covers", f"{book['image_name']}")
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

def display_borrowed_books(self, user_id, borrowed_books_table):
    borrowed_books_collection = self.database_manager.db["borrowed_books"]
    user_borrowed_books = borrowed_books_collection.find({"user_id": user_id})
    borrowed_books_table.setRowCount(0)
    for index, borrowed_book in enumerate(user_borrowed_books):
        # Get book information from the "books" collection based on book_id
        books_collection = self.database_manager.db["books"]
        book_id = borrowed_book["book_id"]
        book_query = {"_id": book_id}
        book = books_collection.find_one(book_query)
        # Insert a new row into the table
        borrowed_books_table.insertRow(index)
        # Display book information in the table
        for col, prop in enumerate(["title", "author", "pages", "year"]):
            borrowed_books_table.setItem(index, col, QTableWidgetItem(str(book[prop])))
        cover_label = QLabel()
        cover_path = os.path.join(Path(__file__).resolve().parent.parent, "book_covers", f"{book['image_name']}")
        if os.path.exists(cover_path):
            pixmap = QPixmap(cover_path)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            cover_label.setPixmap(scaled_pixmap)
            borrowed_books_table.setRowHeight(index, scaled_pixmap.height())
            cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            borrowed_books_table.setCellWidget(index, 4, cover_label)
        else:
            placeholder_label = QLabel("No Image")
            borrowed_books_table.setCellWidget(index, 4, placeholder_label)
        # Display the borrowed date in the sixth column
        borrowed_date = borrowed_book["borrow_date"]
        formatted_borrowed_date = datetime.strftime(borrowed_date, "%d/%m/%Y, %H:%M")
        borrowed_books_table.setItem(index, 5, QTableWidgetItem(formatted_borrowed_date))
        # Display the expiration date in the seventh column
        expiry_date = borrowed_book["expiry_date"]
        formatted_expiry_date = datetime.strftime(expiry_date, "%d/%m/%Y, %H:%M")
        borrowed_books_table.setItem(index, 6, QTableWidgetItem(formatted_expiry_date))
    borrowed_books_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

def display_book_history(self, user_id, history_table):
    history_collection = self.database_manager.db["customer_history"]
    books_collection = self.database_manager.db["books"]
    user_history = history_collection.find({"user_id": user_id})
    history_table.setRowCount(0)
    for history_entry in user_history:
        book_id = history_entry.get("book_id", "")
        # Check if the book exists in the books collection
        book = books_collection.find_one({"_id": book_id})
        if not book:
            continue  # Skip this entry if the book does not exist
        index = history_table.rowCount()
        history_table.insertRow(index)
        image_name = book.get("image_name", "")  
        # Display book information in the corresponding columns
        for col, prop in enumerate(["title", "author", "pages", "year"]):
            history_table.setItem(index, col, QTableWidgetItem(str(book.get(prop, ""))))
        cover_label = QLabel()
        cover_path = os.path.join(Path(__file__).resolve().parent.parent, "book_covers", f"{image_name}")
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
        formatted_event_date = datetime.strftime(history_entry["borrow_date"], "%d/%m/%Y, %H:%M")
        history_table.setItem(index, 5, QTableWidgetItem(formatted_event_date))
    history_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

def search_book_catalog(self, signals, statusBar, catalog_table, refresh_catalog_button, cancel_button):
    role = "Customer"
    label_1 = "Author:"
    label_2 = "Title:"
    label_3 = "Year:"
    label_4 = ""
    dialog = SearchDialog(role, label_1, label_2, label_3, label_4)
    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        author_text = dialog.input_1.text()
        title_text = dialog.input_2.text()
        year_text = dialog.input_3.text()
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
            query["year"] = {"$regex": year_text, "$options": "i"}
            year_formatted =(f"  Year: '{year_text}'")
        if len(author_text) >= 3 or len(title_text) >= 3 or len(year_text) >= 3:
            signals.update_status_bar_widget.emit(f"Showing book searches for: {author_formatted}{title_formatted}{year_formatted}")
            refresh_catalog_button.setEnabled(False)   # Disable the button to refresh search results
            cancel_button.setEnabled(True)    # Disable the button to cancel the search if the search is not in progress
            cursor = books_collection.find(query)
            display_book_catalog(self, catalog_table, cursor)
        else:
            statusBar.showMessage("The minimum character length required for searching is 3.", 8000)
            return 

def sort_book_catalog(self, signals, catalog_table, refresh_catalog_button, cancel_button):
    combo_box_items = ["Title", "Author", "Year"]
    dialog = SortDialog(combo_box_items)
    result = dialog.exec()
    if result == QDialog.DialogCode.Accepted:
        sort_attr = dialog.attribute_combo.currentText().lower()
        sort_ascend =  dialog.ascending_radio.isChecked()
        refresh_catalog_button.setEnabled(False) 
        cancel_button.setEnabled(True)
        books_collection = self.database_manager.db["books"]
        cursor = books_collection.find().sort([(sort_attr, 1 if sort_ascend == True else -1)])
        signals.update_status_bar_widget.emit(f"Books sorted by {sort_attr}")
        display_book_catalog(self, catalog_table, cursor)

def borrow_book(self, catalog_table, user_id, database_manager, statusBar, role):
    # Get the selected row
    selected_row = catalog_table.currentRow()
    number_of_selected_rows = len(catalog_table.selectionModel().selectedRows())
    if number_of_selected_rows == 1:
        # Get book information from the selected row
        title = catalog_table.item(selected_row, 0).text()
        author = catalog_table.item(selected_row, 1).text()
        # Find the user in the database
        users_collection = database_manager.db["users"]
        user_query = {"_id": user_id}
        user_document = users_collection.find_one(user_query)
        # Find the _id of the book based on title and author
        books_collection = database_manager.db["books"]
        book_query = {"title": title, "author": author}
        book_document = books_collection.find_one(book_query)
        # Borrowed books collection
        borrowed_books_collection = database_manager.db["borrowed_books"]
        # Set up messages based on the role
        if role == "Customer":
            message_1 = "Borrow Failed"
            message_2 = "You have already borrowed the maximum allowed number of books (6)."
            message_3 = f"You have already borrowed '{title}' by {author}."
            message_4 = "Borrow a Book"
            message_5 = f"Do you want to borrow '{title}' by {author}?"
            message_6 = f"You have borrowed '{title}' by {author}."
        else:
            message_1 = "Book Asignment Failed"
            message_2 = "This user has already borrowed the maximum allowed number of books (6)."
            message_3 = f"This user already has a book '{title}' by {author} borrowed."
            message_4 = "Asign a Book"
            message_5 = f"Do you want to asign '{title}' by {author}?"
            message_6 = f"You have asigned '{title}' by {author}."
        if not user_document:
            QMessageBox.warning(self, message_1, f"User not found in the database.")
            return
        if not book_document:
            QMessageBox.warning(self, message_1, f"Book not found in the database.")
            return
        else:
            book_id = book_document["_id"]
        # Check if there are items available for borrowing
        items = get_available_items(book_id, books_collection)
        if items <= 0:
            QMessageBox.warning(self, message_1, f"The book '{title}' by {author} is out of stock.")
            return
        # Check if the user has reached the maximum limit of borrowed books (6 books)
        elif is_max_books_borrowed(user_id, borrowed_books_collection):
            QMessageBox.warning(self, "Book Limit Exceeded", message_2)
            return
        # Check if the book is already in the user's borrowed_books
        elif is_book_already_borrowed(user_id, book_id, borrowed_books_collection):
            QMessageBox.warning(self, "Already Borrowed", message_3)
            return
        # Confirm borrowing with the user
        else:
            reply = QMessageBox.question(
                self, message_4, message_5, QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel )
            if reply == QMessageBox.StandardButton.Yes:
                history_collection = database_manager.db["customer_history"]
                borrow_selected_book(user_id, book_id, selected_row, books_collection, borrowed_books_collection, history_collection, catalog_table, statusBar, message_6)
                return True
    else:
        return

def borrow_selected_book(user_id, book_id, selected_row, books_collection, borrowed_books_collection, history_collection, catalog_table, statusBar, message_6):
        # Insert a document into the "borrowed_books" collection
        borrow_date = datetime.utcnow()
        expiry_date = borrow_date + timedelta(days=6) 
        borrowed_book = {
            "user_id": user_id,
            "book_id": book_id,
            "borrow_date": borrow_date,
            "expiry_date": expiry_date
        }
        borrowed_books_collection.insert_one(borrowed_book)
        # Update the "items" field in the "books" collection (decrement by 1)
        update_query = {"$inc": {"items": -1}}
        books_collection.update_one({"_id": book_id}, update_query)
        # Update the "items" column in the catalog_table for the selected row
        updated_items = catalog_table.item(selected_row, 4).text()
        updated_items = str(int(updated_items) - 1) 
        catalog_table.setItem(selected_row, 4, QTableWidgetItem(updated_items))
        statusBar.showMessage(message_6, 8000)
        # Add the book to the user's history
        add_to_user_history(user_id, book_id, borrow_date, history_collection)

def get_available_items(book_id, books_collection):
    book = books_collection.find_one({"_id": book_id})
    if book:
        return book.get("items", 0)  
    else:
        return 0  

def is_max_books_borrowed(user_id, borrowed_books_collection):
    borrowed_books_count = borrowed_books_collection.count_documents(
        {"user_id": user_id}
    )
    return borrowed_books_count >= 6

def is_book_already_borrowed(user_id, book_id, borrowed_books_collection):
    existing_borrowed_book = borrowed_books_collection.find_one(
        {"user_id": user_id, "book_id": book_id}
    )
    return existing_borrowed_book is not None

def add_to_user_history(user_id, book_id, borrow_date, history_collection):
    # Add the book information into the user's history
    history_entry = {
        "user_id": user_id,
        "book_id": book_id,
        "borrow_date": borrow_date,
    }
    history_collection.insert_one(history_entry)
