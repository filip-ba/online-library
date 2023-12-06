from PyQt6.QtWidgets import (
      QWidget, QPushButton, QVBoxLayout, QTabWidget, QMessageBox, QComboBox, QListView, QSpacerItem, QSizePolicy,  
      QInputDialog, QHBoxLayout, QTableWidget, QTableWidgetItem, QLabel, QLineEdit, QGroupBox, QGridLayout )
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from bson import ObjectId
from pathlib import Path
import os
from global_state import GlobalState
from datetime import datetime, timedelta , timezone
from database_manager import DatabaseManager


class ManageConfirmationsTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_tab_ui()
        # Connects

    def create_tab_ui(self):
        pass