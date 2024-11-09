import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from conviction.register import register_user, is_user_registered, get_user_balance
from conviction.pokeDex import fetch_pokemon_data
from config.pokemonView import create_pokemon_embed
from conviction.market import create_market_embed, buy_redeem, view_redeem

#---------
# Load environment variables and fetch coin emojis
#---------
load_dotenv()

SERENE_COIN = os.getenv("SERENE_COIN")
SPECTRA_COIN = os.getenv("SPECTRA_COIN")
TOKEN = os.getenv("DISCORD_TOKEN")

#---------
# Set up bot intents and initialize the bot
#---------
intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

#---------
# Helper function to check if user is registered
#---------
async def check_registration(ctx):
    if not await is_user_registered(ctx):
        await ctx.send(f"Please register first using the `!register` command.")
        return False
    return True

#---------
# Register command for new users
#---------
@bot.command(name="register")
async def register(ctx):
    try:
        await register_user(ctx)
    except Exception as e:
        await ctx.send(f"An error occurred during registration: {e}")
        print(f"Error during registration: {e}")

#---------
# Balance command to display user's coin balance
#---------
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

#---------
# Dex command to fetch Pokémon data and display in an embed
#---------
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

#---------
# Error handling for unexpected errors
#---------
@bot.event
async def on_error(event, *args, **kwargs):
    print(f"Unexpected error occurred: {event}")
    error_message = f"An unexpected error occurred: {event}"

#---------
# Command-specific error handling
#---------
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

#---------
# Market command to display available items for purchase
#---------
@bot.command(name="market")
async def market(ctx):
    try:
        embed = create_market_embed()
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"An error occurred while fetching the market: {e}")
        print(f"Error fetching market: {e}")

#---------
# Buy command to handle market item purchases
#---------
@bot.command(name="buy")
async def buy(ctx, item: str, amount: int = 1):
    if item.lower() == "redeem":
        await buy_redeem(ctx, amount)
    else:
        await ctx.send("Invalid item. Only 'redeem' is available for purchase at the moment.")

#---------
# View redeem command to display the user's current redeems
#---------
@bot.command(name="viewredeem")
async def viewredeem(ctx):
    try:
        await view_redeem(ctx)
    except Exception as e:
        await ctx.send(f"An error occurred while fetching your Redeem count: {e}")
        print(f"Error fetching Redeem count for user {ctx.author.id}: {e}")

# Run the bot
bot.run(TOKEN)
