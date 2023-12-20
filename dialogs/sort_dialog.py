from PyQt6.QtWidgets import (
    QDialog, QLabel, QComboBox, QRadioButton, 
    QPushButton, QVBoxLayout, QHBoxLayout )
from PyQt6.QtCore import Qt


class SortDialog(QDialog):
    def __init__(self, combo_box_items):
        super().__init__()
        self.combo_box_items = combo_box_items
        self.create_dialog_ui()
        # Connects
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def create_dialog_ui(self):
        self.setWindowTitle("Sorting Options")
        self.setFixedSize(400, 200)
        layout = QVBoxLayout()
        title_label = QLabel("Sorting Options")
        title_label.setStyleSheet("font-size: 14pt;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        # Combo box for selecting the attribute
        combo_box_layout = QVBoxLayout()
        attribute_label = QLabel("Select Attribute:")
        self.attribute_combo = QComboBox()
        self.attribute_combo.addItems(self.combo_box_items)
        combo_box_layout.addWidget(attribute_label)
        combo_box_layout.addWidget(self.attribute_combo)
        combo_box_layout.addSpacing(10)
        layout.addLayout(combo_box_layout)
        # Radio buttons 
        radio_and_title_layout = QVBoxLayout()
        order_label = QLabel("Select Order:")
        order_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        radio_and_title_layout.addWidget(order_label)
        radio_layout = QHBoxLayout()
        self.ascending_radio = QRadioButton("Ascending")
        self.descending_radio = QRadioButton("Descending")
        self.ascending_radio.setChecked(True)  
        radio_layout.addWidget(self.ascending_radio)
        radio_layout.addWidget(self.descending_radio)
        radio_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        radio_and_title_layout.addLayout(radio_layout)
        radio_and_title_layout.addSpacing(10)
        layout.addLayout(radio_and_title_layout)
        # Ok and Cancel buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Ok")
        self.cancel_button = QPushButton("Cancel")
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)
        # Set the layout
        self.setLayout(layout)

