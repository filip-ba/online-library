from PyQt6.QtWidgets import ( 
    QDialog, QPushButton, QHeaderView, 
     QVBoxLayout, QHBoxLayout )


class BorrowedBooksDialog(QDialog):
    def __init__(self, user_id, borrowed_books_table):
        super().__init__()
        self.borrowed_books_table = borrowed_books_table
        self.user_id = user_id
        self.create_dialog_ui()
        # Connects
        self.remove_book_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def create_dialog_ui(self):
        self.setWindowTitle("Borrowed Books")
        self.setFixedSize(750, 700)
        layout = QVBoxLayout()
        # Borrowed books table
        self.borrowed_books_table.setColumnCount(7)
        self.borrowed_books_table.setHorizontalHeaderLabels(["Title", "Author", "Pages", "Year", "Book Cover", "Borrow Date", "Due Date"])
        header = self.borrowed_books_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # Buttons
        button_layout = QHBoxLayout()
        self.remove_book_button  = QPushButton("Remove a Book")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.remove_book_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        # Layout
        layout.addWidget(self.borrowed_books_table)
        layout.addLayout(button_layout)
        self.setLayout(layout)
