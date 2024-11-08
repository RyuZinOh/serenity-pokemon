import discord
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Map to generate region names dynamically based on generation
GENERATION_REGION_MAP = {
    "generation-i": "Kanto",
    "generation-ii": "Johto",
    "generation-iii": "Hoenn",
    "generation-iv": "Sinnoh",
    "generation-v": "Unova",
    "generation-vi": "Kalos",
    "generation-vii": "Alola",
    "generation-viii": "Galar",
    "generation-ix": "Paldea"
}

# Dynamically fetch type emojis
TYPE_EMOJI_MAP = {key: os.getenv(f"{key.upper()}_TYPE_EMOJI", "") for key in [
    "electric", "fire", "water", "grass", "psychic", "rock", "ghost", "normal",
    "fairy", "dark", "dragon", "ice", "steel", "fighting", "bug", "poison", "flying", "ground"
]}

def create_pokemon_embed(pokemon_data):
    general_data, species_data = pokemon_data["general"], pokemon_data["species"]
    
    name = general_data["name"].capitalize()
    types = [t["type"]["name"] for t in general_data["types"]]
    height, weight = general_data["height"] / 10, general_data["weight"] / 10
    sprite = general_data["sprites"]["other"]["official-artwork"]["front_default"]
    
    description = next((entry["flavor_text"].replace("\n", " ") for entry in species_data["flavor_text_entries"]
                        if entry["language"]["name"] == "en"), "No description available.")
    
    names = [
        f":flag_jp: {species_data['names'][0]['name']}",
        f":flag_gb: {name}"
    ]
    
    stats = {stat["stat"]["name"].capitalize(): stat["base_stat"] for stat in general_data["stats"]}
    total_stats = sum(stats.values())

    evolution_chain = []
    current_stage = requests.get(species_data["evolution_chain"]["url"]).json()["chain"]
    
    while current_stage:
        evo_name = current_stage["species"]["name"].capitalize()
        if current_stage["evolves_to"]:
            next_stage = current_stage["evolves_to"][0]
            trigger = next_stage["evolution_details"][0].get("trigger", {}).get("name", "level up")
            evolution_chain.append(f"{evo_name} → {next_stage['species']['name'].capitalize()} ({trigger})")
            current_stage = next_stage
        else:
            evolution_chain.append(evo_name)
            break

    region = GENERATION_REGION_MAP.get(species_data["generation"]["name"], "Unknown")
    is_catchable = "Yes" if general_data.get("is_default", True) else "No"
    
    embed = discord.Embed(
        title=f"{name} - Pokédex",
        description=description,
        color=discord.Color.green()
    )
    
    embed.add_field(name="Evolution", value="\n".join(evolution_chain), inline=False)
    
    type_emoji = " ".join([TYPE_EMOJI_MAP.get(t, "") for t in types])

    embed.add_field(name="Types", value=type_emoji, inline=True)
    
    embed.add_field(name="Region", value=region, inline=True)
    embed.add_field(name="Catchable", value=is_catchable, inline=True)

    stats_field = "\n".join([f"{k}: {v}" for k, v in stats.items()])
    embed.add_field(name="Base Stats", value=f"{stats_field}\n**Total**: {total_stats}", inline=False)

    embed.add_field(name="Appearance", value=f"Height: {height} m\nWeight: {weight} kg", inline=True)
    embed.add_field(name="Names", value="\n".join(names), inline=False)
    embed.set_image(url=sprite)
    
    return embed
