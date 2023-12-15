from PyQt6.QtWidgets import QApplication
from main_window import MainWindow
from database_manager import DatabaseManager

def main():
    connection_string = "mongodb+srv://admin:admin@cluster0.p8pwbsz.mongodb.net/?retryWrites=true&w=majority"
    database_name = "OnlineLibrary"
    database_manager = DatabaseManager(connection_string, database_name)
    app = QApplication([])
    app.aboutToQuit.connect(database_manager.close_connection)
    window = MainWindow(database_manager)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
