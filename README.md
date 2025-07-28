# Online Library Application

<img src="icon.ico" width="100">


## Description
This application was created as a final project for the Advanced Database Systems course. It is a simple desktop application for managing an online library. The application is written in Python with PyQt6 using MongoDB atlas for persistent storage. 

## Features

### Librarian

- **User Management:**
  - Add, edit, ban and unban user accounts.
  - Track user history and borrowed books.
  - Approval of accounts awaiting activation or changes.
  - Assign or remove books to users.
  - Search and sort the list of customers.

- **Book Management:**
  - Maintain a comprehensive book inventory.
  - Easily add, edit, or remove books from the collection.
  - Search and sort the book catalog.
 
- **Export and Import Functionality:**
  - Export library data to JSON files for backup or sharing.
  - Import data from JSON files to restore or update the library database.

### Customer

- **Functions for the customer:**
  - Borrow and return books.
  - Search and sort the book catalog.
  - Edit account details.
  - Keep a record of borrowed books history and currently borrowed books, including borrow dates and expiry dates.

## Screenshots

<div style="display: flex; justify-content: space-between;">
  <img src="screenshots/screenshot1.png" width="750">
  <img src="screenshots/screenshot2.png" width="750">
</div>
<div style="display: flex; justify-content: space-between;">
  <img src="screenshots/screenshot3.png" width="750">
  <img src="screenshots/screenshot4.png" width="750">
</div>

## Installation

### Prerequisites

- Python (version 3.12)
- PyQt (version 6)
- MongoDB 

### How to Install
#### To try this application you need to create your own database and collections.

1. Create a MongoDB database called "OnlineLibrary". You can either use MongoDB locally or MongoDB Atlas.
2. Create the following collections(don't change the names!): "books", "users", "librarians", "borrowed_books", "customer_history", "inactivated_accounts", "edited_accounts", "banned_accounts"
3. Replace the "connection_string" in the main.py.
4. Run the application: `python main.py`
