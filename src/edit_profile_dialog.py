from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

class EditProfileDialog(QDialog):
    def __init__(self, current_user_info, parent=None):
        super().__init__(parent)
        self.current_user_info = current_user_info
        self.create_dialog_ui()

    def create_dialog_ui(self):
        self.setWindowTitle("Edit Profile")
        layout = QVBoxLayout()
        # Add labels and line edits for each field
        name_layout = self.create_field_layout("First Name:", self.current_user_info.get("first_name", ""))
        last_name_layout = self.create_field_layout("Last Name:", self.current_user_info.get("last_name", ""))
        ssn_layout = self.create_field_layout("SSN:", self.current_user_info.get("ssn", ""))
        address_layout = self.create_field_layout("Address:", self.current_user_info.get("address", ""))

        layout.addLayout(name_layout)
        layout.addLayout(last_name_layout)
        layout.addLayout(ssn_layout)
        layout.addLayout(address_layout)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        # Connect signals
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        self.setLayout(layout)

    def create_field_layout(self, label_text, initial_value):
        field_layout = QVBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setText(initial_value)
        field_layout.addWidget(label)
        field_layout.addWidget(line_edit)
        return field_layout
