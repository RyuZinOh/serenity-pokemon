from pymongo import MongoClient

class MongoDB:
    def __init__(self, uri="mongodb://localhost:27017/", db_name="serenity"):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
    
    def get_collection(self,name):
        return self.db[name]
    
# Global database instance
db_instance = MongoDB()
