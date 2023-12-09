from PyQt6.QtWidgets import ( 
    QDialog, QLabel, QLineEdit, QPushButton, QSpacerItem, 
    QHBoxLayout, QVBoxLayout, QFormLayout, QFileDialog )
from PyQt6.QtGui import QRegularExpressionValidator, QIntValidator
from PyQt6.QtCore import Qt, QRegularExpression, QFileInfo
from PyQt6.QtWidgets import QFileDialog


class AddBookDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.create_dialog_ui()
        # Connects
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        # Variables for importing the image
        self.image_name = ""
        self.path_name = ""

    def create_dialog_ui(self):
        self.setWindowTitle("Add New Book")
        self.setFixedSize(500, 300)    
        layout = QVBoxLayout()
        window_title_label = QLabel("Add New Book")
        window_title_label.setStyleSheet("font-size: 14pt;")
        window_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(window_title_label)
        # Form layout
        form_layout = QFormLayout()
        # Title
        title_label = QLabel("Title:")
        self.title_input = QLineEdit()
        self.title_input.setMaxLength(60)
        form_layout.addRow(title_label, self.title_input)
        # Author
        author_label = QLabel("Author:")
        self.author_input = QLineEdit()
        self.author_input.setValidator(QRegularExpressionValidator(QRegularExpression("[A-Za-z ]+")))
        self.author_input.setMaxLength(60)
        form_layout.addRow(author_label, self.author_input)
        # Pages
        pages_label = QLabel("Pages:")
        self.pages_input = QLineEdit()
        self.pages_input.setValidator(QIntValidator())  
        self.pages_input.setMaxLength(4)
        form_layout.addRow(pages_label, self.pages_input)
        # Year
        year_label = QLabel("Year:")
        self.year_input = QLineEdit()
        self.year_input.setValidator(QIntValidator())  
        self.year_input.setMaxLength(4)
        form_layout.addRow(year_label, self.year_input)
        # Items
        items_label = QLabel("Items:")
        self.items_input = QLineEdit()
        self.items_input.setValidator(QIntValidator())  
        self.items_input.setMaxLength(2)
        form_layout.addRow(items_label, self.items_input)
        # Import Image
        import_layout_1 = QHBoxLayout()
        import_layout_2 = QHBoxLayout()
        import_layout_2.setContentsMargins(5, 0, 0, 0)
        import_layout_1.setContentsMargins(0, 0, 0, 10)
        self.image_name_label = QLabel("File: ")
        self.import_button = QPushButton("Import Image")
        self.import_image_label = QLabel("Image: ")
        import_layout_1.addWidget(self.import_image_label)
        import_layout_2.addWidget(self.import_button)
        import_layout_2.addWidget(self.image_name_label)
        import_layout_1.addLayout(import_layout_2)
        import_layout_1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.import_button.clicked.connect(self.get_image_name)
        # Adding layouts into the main layout
        form_layout.setSpacing(10)  # Adding a space between the forms
        layout.addLayout(form_layout)
        layout.addSpacerItem(QSpacerItem(10, 10))   # Adding a space after the form layout
        layout.addLayout(import_layout_1)
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        # Set the layout
        self.setLayout(layout)

    def get_image_name(self):
        self.path_name, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.bmp)")
        if self.path_name:
            self.image_name = QFileInfo(self.path_name).fileName()
            self.image_name_label.setText(f"File: {self.image_name}")
        else:
            return
 
