import requests

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

def fetch_pokemon_data(pokemon_name):
    try:
        url = f"{POKEAPI_BASE_URL}{pokemon_name.lower()}"
        response = requests.get(url)
        if response.ok:
            data = response.json()
            species_data = requests.get(data["species"]["url"]).json()
            return {"general": data, "species": species_data}
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Pokémon data: {e}")
        return None
