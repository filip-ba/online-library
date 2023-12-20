from PyQt6.QtWidgets import (
      QWidget, QTabWidget, QHBoxLayout )
from database_manager import DatabaseManager
from librarian.manage_books_tab import ManageBooksTab
from librarian.manage_customers_tab import ManageCustomersTab


class LibrarianTab(QWidget):
    def __init__(self, database_manager: DatabaseManager, statusBar, signals):
        super().__init__()
        self.database_manager = database_manager
        self.signals = signals
        self.statusBar = statusBar
        self.create_librarian_ui()

    def create_librarian_ui(self):
        main_layout = QHBoxLayout()  
        self.tab_widget = QTabWidget(self)
        manage_books_tab = ManageBooksTab(self.database_manager, self.statusBar, self.signals)
        manage_customers_tab = ManageCustomersTab(self.database_manager, self.statusBar, self.signals)
        self.tab_widget.addTab(manage_books_tab, "Manage Books")
        self.tab_widget.addTab(manage_customers_tab, "Manage Customers")
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

            



