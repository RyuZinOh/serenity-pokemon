import requests

POKEAPI_BASE_URL = "https://pokeapi.co/api/v2/pokemon/"

def get_pokemon_data(pokemon_name):
    url = POKEAPI_BASE_URL + pokemon_name.lower()
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        species_data = requests.get(data["species"]["url"]).json()
        return {
            "general": data,
            "species": species_data
        }
    else:
        return None
