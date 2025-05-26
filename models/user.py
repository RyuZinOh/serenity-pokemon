from datetime import datetime, timezone
from config.connectDB import db_instance

class UserModel:
    def __init__(self):
        self.collection = db_instance.get_collection("users")

    def create_user(self, discord_id, username):
        user_data ={
            "discord_id": str(discord_id),
            "username": username,
            "joined_at": datetime.now(timezone.utc),
        }
        return self.collection.insert_one(user_data)
    
    def get_user(self, discord_id):
        return self.collection.find_one({"discord_id": str(discord_id)})
    
    def user_exists(self, discord_id):
        return self.collection.count_documents({"discord_id":str(discord_id)})>0

