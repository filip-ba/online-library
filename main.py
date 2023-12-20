from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from database_manager import DatabaseManager

def main():
    connection_string = ""    # Replace this with your connection string
    database_name = "OnlineLibrary"
    database_manager = DatabaseManager(connection_string, database_name)
    app = QApplication([])
    app.aboutToQuit.connect(database_manager.close_connection)
    window = MainWindow(database_manager)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
