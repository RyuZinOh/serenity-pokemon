from pymongo import MongoClient

class MongoDB:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="bot_data"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.users_collection = self.db["users"]
    
    def get_users_collection(self):
        return self.users_collection
    
# Global database instance
db_instance = MongoDB()
