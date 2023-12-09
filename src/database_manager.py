from pymongo import MongoClient


class DatabaseManager:
    def __init__(self, connection_string, database_name):
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]

    def close_connection(self):
        self.client.close()