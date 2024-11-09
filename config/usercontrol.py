import discord
from config.connectDB import db_instance
from conviction.pokeDex import fetch_pokemon_data
from conviction.market import buy_redeem, view_redeem
from conviction.register import get_user_balance, is_user_registered
import random

#-------------
# Function to generate random IVs for redeemed Pokémon
#-------------
def generate_random_ivs():
    return {stat: random.randint(0, 31) for stat in ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]}

#-------------
# Check if user is registered before proceeding
#-------------
async def check_registration(ctx):
    if not await is_user_registered(ctx):
        await ctx.send("Please register first using the `!register` command.")
        return False
    return True

#-------------
# Redeem a Pokémon and update the user's data accordingly
#-------------
async def redeem(ctx, pokemon_name):
    if not await check_registration(ctx):
        return
    
    users_collection = db_instance.get_users_collection()
    user_data = users_collection.find_one({"user_id": ctx.author.id})

    if not user_data or user_data.get("redeems", 0) <= 0:
        await ctx.send("You don't have any redeems left. Please buy a redeem from the market!")
        return

    pokemon_data = fetch_pokemon_data(pokemon_name)
    if not pokemon_data:
        await ctx.send("Pokemon not found!")
        return

    general_data = pokemon_data["general"]
    name = general_data["name"].capitalize()
    types = [t["type"]["name"] for t in general_data["types"]]
    height, weight = general_data["height"] / 10, general_data["weight"] / 10
    sprite = general_data["sprites"]["other"]["official-artwork"]["front_default"]
    
    embed = discord.Embed(
        title=f"Wild {name} Appeared!",
        description=f"A wild **{name}** has appeared! 🎉",
        color=discord.Color.green()
    )
    embed.add_field(name="Types", value=" ".join(types), inline=True)
    embed.add_field(name="Height", value=f"{height} m", inline=True)
    embed.add_field(name="Weight", value=f"{weight} kg", inline=True)
    embed.set_image(url=sprite)

    await ctx.send(embed=embed)

    redeemed_pokemon = {
        "name": name,
        "types": types,
        "sprite": sprite,
        "iv": generate_random_ivs()
    }

    users_collection.update_one(
        {"user_id": ctx.author.id},
        {"$set": {"redeemed_pokemon": redeemed_pokemon}, "$inc": {"redeems": -1}}
    )
    await ctx.send(f"Successfully redeemed **{name}**! Ready to catch it!")

#-------------
# Catch a Pokémon and add it to the user's inventory
#-------------
async def catch(ctx, pokemon_name: str):
    try:
        users_collection = db_instance.get_users_collection()
        user_data = users_collection.find_one({"user_id": ctx.author.id})
        
        if not user_data:
            await ctx.send("Please register first using the `!register` command.")
            return
        
        redeemed_pokemon = user_data.get("redeemed_pokemon", None)

        if not redeemed_pokemon:
            await ctx.send("You don't have a Pokémon ready to be caught. Please redeem a Pokémon first!")
            return
        
        correct_pokemon_name = redeemed_pokemon["name"].lower()

        if pokemon_name.lower() != correct_pokemon_name:
            await ctx.send(f"Oops! The Pokémon name is incorrect. The correct name is **{correct_pokemon_name.capitalize()}**.")
            return
        
        caught_pokemon = {
            "name": redeemed_pokemon["name"],
            "types": redeemed_pokemon["types"],
            "sprite": redeemed_pokemon["sprite"],
            "iv": redeemed_pokemon["iv"]
        }

        users_collection.update_one(
            {"user_id": ctx.author.id},
            {"$push": {"inventory": caught_pokemon}, "$unset": {"redeemed_pokemon": ""}}
        )

        await ctx.send(f"Congratulations {ctx.author.name}! You caught **{redeemed_pokemon['name']}**! 🎉")
    except Exception as e:
        await ctx.send(f"An error occurred while catching the Pokémon: {e}")
        print(f"Error catching Pokémon: {e}")

#-------------
# Show user's Pokémon information from their inventory
#-------------
async def info(ctx, poke_id: int):
    try:
        user_data = await get_user_data(ctx.author.id)
        if not user_data or not user_data.get("inventory"):
            await ctx.send(f"Hi {ctx.author.name}, you don't have any Pokémon in your inventory yet!")
            return
        
        inventory = user_data["inventory"]
        
        if not (1 <= poke_id <= len(inventory)):
            await ctx.send(f"Invalid Pokémon ID. Please provide a valid number from 1 to {len(inventory)}.")
            return
        
        pokemon = inventory[poke_id - 1]
        name = pokemon["name"]
        ivs = pokemon["iv"]
        sprite = pokemon["sprite"]
        types = pokemon.get("types", ["Unknown"])
        total_iv_percent = calculate_iv_percentage(ivs)
        
        ivs_field = "\n".join([f"{stat.capitalize()}: {ivs[stat]}/31" for stat in ivs])
        types_field = ", ".join(types)
        
        embed = discord.Embed(title=f"{name} - Pokémon Stats", color=discord.Color.green())
        embed.set_image(url=sprite)
        embed.set_footer(text=f"Requested by {ctx.author.name}")
        embed.set_thumbnail(url=ctx.author.avatar.url)  # Setting user avatar as thumbnail

        embed.add_field(name="Types", value=types_field, inline=False)
        embed.add_field(name="IVs", value=ivs_field, inline=False)
        embed.add_field(name="Total IV%", value=f"{total_iv_percent}%", inline=False)

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send("Oops! Something went wrong while fetching Pokémon info.")
        print(f"Error fetching info for user {ctx.author.id}: {e}")

#-------------
# Show the user's Pokémon inventory
#-------------
async def p(ctx):
    try:
        user_data = await get_user_data(ctx.author.id)
        if not user_data or not user_data.get("inventory"):
            await ctx.send(f"Hi {ctx.author.name}, you don't have any Pokémon in your inventory yet!")
            return
        
        inventory = user_data["inventory"]
        if not inventory:
            await ctx.send(f"Your Pokémon inventory is empty, {ctx.author.name}.")
            return
        
        embed = discord.Embed(title=f"{ctx.author.name}'s Pokémon Inventory", color=discord.Color.blue())
        embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

        for idx, pokemon in enumerate(inventory):
            name = pokemon["name"]
            ivs = pokemon["iv"]
            total_iv_percent = calculate_iv_percentage(ivs)
            embed.add_field(
                name=f"{idx+1}. {name} - {total_iv_percent}% Total IV",
                value=f"ID: {idx+1}", inline=False
            )
        
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send("Oops! Something went wrong while fetching your inventory.")
        print(f"Error fetching inventory for user {ctx.author.id}: {e}")

#-------------
# Helper function to get user data from database
#-------------
async def get_user_data(user_id):
    try:
        users_collection = db_instance.get_users_collection()
        return users_collection.find_one({"user_id": user_id})
    except Exception as e:
        print(f"Error fetching user data for {user_id}: {e}")
        return None

#-------------
# Helper function to calculate IV percentage for Pokémon
#-------------
def calculate_iv_percentage(ivs):
    total_iv = sum(ivs.values())
    return round((total_iv / 186) * 100, 2)
