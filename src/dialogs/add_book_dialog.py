from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QSpinBox, QPushButton, QVBoxLayout, QHBoxLayout


class AddBookDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.create_dialog_ui()
        # Connects
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def create_dialog_ui(self):
        self.setWindowTitle("Add New Book")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        # Title
        title_layout = QHBoxLayout()
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)
        # Author
        author_layout = QHBoxLayout()
        author_label = QLabel("Author:")
        self.author_input = QLineEdit()
        author_layout.addWidget(author_label)
        author_layout.addWidget(self.author_input)
        layout.addLayout(author_layout)
        # Pages
        pages_layout = QHBoxLayout()
        pages_label = QLabel("Pages:")
        self.pages_input = QSpinBox()
        self.pages_input.setMinimum(1)
        pages_layout.addWidget(pages_label)
        pages_layout.addWidget(self.pages_input)
        layout.addLayout(pages_layout)
        # Year
        year_layout = QHBoxLayout()
        year_label = QLabel("Year:")
        self.year_input = QLineEdit()
        year_layout.addWidget(year_label)
        year_layout.addWidget(self.year_input)
        layout.addLayout(year_layout)
        # Items
        items_layout = QHBoxLayout()
        items_label = QLabel("Items:")
        self.items_input = QSpinBox()
        self.items_input.setMinimum(1)
        items_layout.addWidget(items_label)
        items_layout.addWidget(self.items_input)
        layout.addLayout(items_layout)
        # Image Name
        image_layout = QHBoxLayout()
        image_label = QLabel("Image Name:")
        self.image_input = QLineEdit()
        image_layout.addWidget(image_label)
        image_layout.addWidget(self.image_input)
        layout.addLayout(image_layout)
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        # Set the layout
        self.setLayout(layout)

