from pymongo import MongoClient

class DatabaseConnectionError(Exception):
    pass

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["user_database"]
    users_collection = db["users"]
except Exception as e:
    raise DatabaseConnectionError("Failed to connect to the database.")