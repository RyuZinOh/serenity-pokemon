import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from conviction.register import register_user, is_user_registered, get_user_balance
from conviction.pokeDex import fetch_pokemon_data
from config.pokemonView import create_pokemon_embed
from conviction.market import create_market_embed, buy_redeem, view_redeem
from config.connectDB import db_instance
from config.usercontrol import redeem, catch, p, info
import random

load_dotenv()

SERENE_COIN = os.getenv("SERENE_COIN")
SPECTRA_COIN = os.getenv("SPECTRA_COIN")
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

async def check_registration(ctx):
    if not await is_user_registered(ctx):
        await ctx.send(f"Please register first using the `!register` command.")
        return False
    return True

@bot.command(name="register")
async def register(ctx):
    try:
        await register_user(ctx)
    except Exception as e:
        await ctx.send(f"An error occurred during registration: {e}")
        print(f"Error during registration: {e}")

@bot.command(name="balance")
async def balance(ctx):
    try:
        if not await check_registration(ctx):
            return

        serene, spectra = await get_user_balance(ctx)
        if serene is None or spectra is None:
            await ctx.send("You are not registered, please use the `!register` command.")
            return
        
        embed = discord.Embed(title=f"{ctx.author.name}'s Balance", color=discord.Color.blue())
        embed.add_field(name="Serene", value=f"{serene} {SERENE_COIN}", inline=False)
        embed.add_field(name="Spectra", value=f"{spectra} {SPECTRA_COIN}", inline=False)
        embed.set_thumbnail(url=ctx.author.avatar.url)

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred while fetching your balance: {e}")
        print(f"Error fetching balance for user {ctx.author.id}: {e}")

@bot.command(name="dex")
async def dex(ctx, pokemon_name):
    try:
        if not await check_registration(ctx):
            return 
        
        pokemon_data = fetch_pokemon_data(pokemon_name)
        if pokemon_data:
            embed = create_pokemon_embed(pokemon_data)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Pokémon not found!")
    except Exception as e:
        await ctx.send(f"An error occurred while fetching Pokémon data: {e}")
        print(f"Error fetching Pokémon data: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Unexpected error occurred: {event}")
    error_message = f"An unexpected error occurred: {event}"

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Missing arguments. Please check the command usage.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Unknown command. Please check the available commands.")
    elif isinstance(error, commands.BotMissingPermissions):
        await ctx.send("I do not have permission to perform that action.")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("You must be registered to use this command!")
    else:
        await ctx.send(f"An error occurred: {error}")
        print(f"Error: {error}")

@bot.command(name="market")
async def market(ctx):
    try:
        embed = create_market_embed()
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred while fetching the market: {e}")
        print(f"Error fetching market: {e}")

@bot.command(name="buy")
async def buy(ctx, item: str, amount: int = 1):
    if item.lower() == "redeem":
        await buy_redeem(ctx, amount)
    else:
        await ctx.send("Invalid item. Only 'redeem' is available for purchase at the moment.")

@bot.command(name="viewredeem")
async def viewredeem(ctx):
    try:
        await view_redeem(ctx)
    except Exception as e:
        await ctx.send(f"An error occurred while fetching your Redeem count: {e}")
        print(f"Error fetching Redeem count for user {ctx.author.id}: {e}")

redeemed_pokemon = {}



@bot.command(name="redeem")
async def redeem_command(ctx, pokemon_name):
    await redeem(ctx, pokemon_name)

@bot.command(name="catch")
async def catch_command(ctx, pokemon_name: str):
    await catch(ctx, pokemon_name)

@bot.command(name="p")
async def pokemon_command(ctx):
    await p(ctx)

@bot.command(name="info")
async def info_command(ctx, poke_id: int):
    await info(ctx, poke_id)

# def generate_random_ivs():
#     return {stat: random.randint(0, 31) for stat in ["hp", "attack", "defense", "special_attack", "special_defense", "speed"]}

# # @bot.command(name="redeem")
# # async def redeem(ctx, pokemon_name):
# #     try:
# #         if not await check_registration(ctx):
# #             return
        
# #         users_collection = db_instance.get_users_collection()
# #         user_data = users_collection.find_one({"user_id": ctx.author.id})
        
# #         if not user_data or user_data.get("redeems", 0) <= 0:
# #             await ctx.send("You don't have any redeems left. Please buy a redeem from the market!")
# #             return

# #         pokemon_data = fetch_pokemon_data(pokemon_name)

# #         if pokemon_data:
# #             general_data = pokemon_data["general"]
            
# #             name = general_data["name"].capitalize()
# #             types = [t["type"]["name"] for t in general_data["types"]]
# #             height, weight = general_data["height"] / 10, general_data["weight"] / 10
# #             sprite = general_data["sprites"]["other"]["official-artwork"]["front_default"]
            
# #             embed = discord.Embed(
# #                 title=f"Wild {name} Appeared!",
# #                 description=f"A wild **{name}** has appeared! 🎉",
# #                 color=discord.Color.green()
# #             )
            
# #             embed.add_field(name="Types", value=" ".join(types), inline=True)
# #             embed.add_field(name="Height", value=f"{height} m", inline=True)
# #             embed.add_field(name="Weight", value=f"{weight} kg", inline=True)
# #             embed.set_image(url=sprite)

# #             await ctx.send(embed=embed)
            
# #             redeemed_pokemon[ctx.author.id] = {
# #                 "name": name,
# #                 "types": types,
# #                 "sprite": sprite,
# #                 "iv": generate_random_ivs()
# #             }

# #             users_collection.update_one({"user_id": ctx.author.id}, {"$inc": {"redeems": -1}})
# #         else:
# #             await ctx.send("Pokémon not found!")
# #     except Exception as e:
# #         await ctx.send(f"An error occurred while redeeming the Pokémon: {e}")
# #         print(f"Error redeeming Pokémon: {e}")

# # @bot.command(name="catch")
# # async def catch(ctx, pokemon_name: str):
# #     try:
# #         # Check if the user has a redeemed Pokémon to catch
# #         if ctx.author.id not in redeemed_pokemon:
# #             await ctx.send("You haven't redeemed any Pokémon yet! Please redeem one first using !redeem.")
# #             return
        
# #         # Get the spawned Pokémon from memory
# #         pokemon = redeemed_pokemon[ctx.author.id]
# #         correct_pokemon_name = pokemon["name"].lower()

# #         # Check if the user entered the correct Pokémon name
# #         if pokemon_name.lower() != correct_pokemon_name:
# #             await ctx.send(f"Oops! The Pokémon name is incorrect. The correct name is **{correct_pokemon_name.capitalize()}**.")
# #             return
        
# #         # Add the Pokémon to the user's inventory in the database
# #         users_collection = db_instance.get_users_collection()
# #         user_data = users_collection.find_one({"user_id": ctx.author.id})
        
# #         if user_data:
# #             # Add Pokémon to the inventory
# #             caught_pokemon = {
# #                 "name": pokemon["name"],
# #                 "types": pokemon["types"],
# #                 "sprite": pokemon["sprite"],
# #                 "iv": pokemon["iv"]
# #             }
            
# #             # Update user's Pokémon collection (inventory)
# #             users_collection.update_one(
# #                 {"user_id": ctx.author.id},
# #                 {"$push": {"inventory": caught_pokemon}}
# #             )

# #             # Remove the redeemed Pokémon from memory
# #             del redeemed_pokemon[ctx.author.id]

# #             # Notify the user
# #             await ctx.send(f"Congratulations {ctx.author.name}! You caught **{pokemon['name']}**! 🎉")
# #         else:
# #             await ctx.send("User data not found in the database.")
# #     except Exception as e:
# #         await ctx.send(f"An error occurred while catching the Pokémon: {e}")
# #         print(f"Error catching Pokémon: {e}")


# # @bot.command(name="p")
# # async def pokemon(ctx):
# #     try:
# #         user_data = await get_user_data(ctx.author.id)
# #         if not user_data:
# #             await ctx.send(f"Hi {ctx.author.name}, you don't have any Pokémon in your inventory yet!")
# #             return
        
# #         inventory = user_data.get("inventory", [])
# #         if not inventory:
# #             await ctx.send(f"Your Pokémon inventory is empty, {ctx.author.name}.")
# #             return
        
# #         embed = discord.Embed(title=f"{ctx.author.name}'s Pokémon Inventory", color=discord.Color.blue())
# #         embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

# #         for idx, pokemon in enumerate(inventory):
# #             name = pokemon["name"]
# #             ivs = pokemon["iv"]
# #             total_iv_percent = calculate_iv_percentage(ivs)
# #             embed.add_field(
# #                 name=f"{idx+1}. {name} - {total_iv_percent}% Total IV",
# #                 value=f"ID: {idx+1}", inline=False
# #             )
        
# #         await ctx.send(embed=embed)
# #     except Exception as e:
# #         await ctx.send("Oops! Something went wrong while fetching your inventory.")
# #         print(f"Error fetching inventory for user {ctx.author.id}: {e}")

# # async def get_user_data(user_id):
# #     try:
# #         users_collection = db_instance.get_users_collection()
# #         return users_collection.find_one({"user_id": user_id})
# #     except Exception as e:
# #         print(f"Error fetching user data for {user_id}: {e}")
# #         return None

# # def calculate_iv_percentage(ivs):
# #     total_iv = sum(ivs.values())
# #     return round((total_iv / 186) * 100, 2)

# # @bot.command(name="info")
# # async def info(ctx, poke_id: int):
# #     try:
# #         user_data = await get_user_data(ctx.author.id)
# #         if not user_data:
# #             await ctx.send(f"Hi {ctx.author.name}, you don't have any Pokémon in your inventory yet!")
# #             return
        
# #         inventory = user_data.get("inventory", [])
# #         if not inventory:
# #             await ctx.send(f"Your Pokémon inventory is empty, {ctx.author.name}.")
# #             return

# #         if poke_id < 1 or poke_id > len(inventory):
# #             await ctx.send(f"Oops! Invalid Pokémon ID. Please provide a valid number from 1 to {len(inventory)}.")
# #             return
        
# #         pokemon = inventory[poke_id - 1]
# #         name = pokemon["name"]
# #         ivs = pokemon["iv"]
# #         sprite = pokemon["sprite"]
# #         types = pokemon.get("types", [])
        
# #         total_iv_percent = calculate_iv_percentage(ivs)

# #         ivs_field = "\n".join([f"{stat.capitalize()}: {ivs[stat]}/31" for stat in ivs])

# #         types_field = ", ".join(types) if types else "Unknown"
        
# #         embed = discord.Embed(title=f"{name} - Pokémon Stats", color=discord.Color.green())
# #         embed.set_image(url=sprite)
# #         embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

# #         embed.add_field(name="Types", value=types_field, inline=False)
# #         embed.add_field(name="IVs", value=ivs_field, inline=False)
# #         embed.add_field(name="Total IV%", value=f"{total_iv_percent}%", inline=False)

# #         # Setting the user's avatar as a larger image on the right side
# #         embed.set_thumbnail(url=ctx.author.avatar.url)

# #         await ctx.send(embed=embed)
# #     except Exception as e:
# #         await ctx.send("Oops! Something went wrong while fetching Pokémon info.")
# #         print(f"Error fetching info for user {ctx.author.id}: {e}")



bot.run(TOKEN)
