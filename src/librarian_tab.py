from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QComboBox,  
      QInputDialog, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from bson import ObjectId
from pathlib import Path
import os
from database_manager import DatabaseManager
from global_state import GlobalState
from datetime import datetime, timedelta , timezone


class LibrarianTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_librarian_ui()
        # Singals
        self.signals.librarian_tab_state.connect(self.set_tab_state)
        self.signals.librarian_logged_in.connect(self.init_librarian_tab)
        # Connects

    def init_librarian_tab(self):
        pass

    def set_tab_state(self, state):
        # Disable/enable widgets in customer_tab depending on whether the user is logged in or not
        if state == False: 
            pass

    def create_librarian_ui(self):
        pass

