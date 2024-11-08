from pymongo import MongoClient

def connect_mongo():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        
        db = client["bot_data"]
        
        users_collection = db["users"]
        
        print("MongoDB connected successfully")
        return users_collection

    except Exception as e:
        print(f"An error occurred: {e}")
        return None
