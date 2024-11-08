import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from conviction.register import register_user  
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
from conviction.pokeDex import get_pokemon_data
from config.pokemonView import create_pokemon_embed

intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command(name="register")
async def register(ctx):
    await register_user(ctx)  
@bot.command(name="dex")
async def dex(ctx, pokemon_name):
    pokemon_data = get_pokemon_data(pokemon_name)
    if pokemon_data:
        embed = create_pokemon_embed(pokemon_data)
        await ctx.send(embed=embed)
    else:
        await ctx.send("Pokémon not found!")

bot.run(TOKEN)
