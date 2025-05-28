from datetime import datetime, timezone
from config.connectDB import db_instance

class CurrencyModel:
    def __init__(self):
        self.collection = db_instance.get_collection("currency")

    def create_vault(self, discord_id):
        vault_data ={
            "discord_id": str(discord_id),
            "spectra_coin":0 ,
            "sera_token" :0,
            "last_updated": datetime.now(timezone.utc)
        }    
        return self.collection.insert_one(vault_data)
    
        
