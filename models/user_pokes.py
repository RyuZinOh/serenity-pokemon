from datetime import datetime, timezone
from config.connectDB import db_instance

class UserPokeModel:
    def __init__(self):
        self.collection = db_instance.get_collection("user_pokemons")
        
    def create_user_pokes(self, discord_id):
        store_data = {
            "discord_id": str(discord_id),
            "pokemons":[],
            "created_at": datetime.now(timezone.utc),
            "last_updated": datetime.now(timezone.utc)
        }
        return self.collection.insert_one(store_data)
    
    def add_pokemon(self, discord_id, pokemon_data):
        fields = {"name", "leverl", "stats"}
        stats = {
            "hp",
            "attack",
            "speical_attack",
            "defense",
            "special_defense",
            "speed"
        }
        if not fields.issubset(pokemon_data):
            raise ValueError("Missing required Fields.")
        if not stats.issubset(pokemon_data["stats"]):
            raise ValueError("Incomplete stats.")
        
        pokemon_data["caught_at"] = datetime.now(timezone.utc)

        return self.collection.update_one(
            {
                "discord_id":str(discord_id)
            },
            {
                "$push":{"pokemons":pokemon_data},
                "$set":{"last_updated": datetime.now(timezone.utc)}
             }
        )
    
    