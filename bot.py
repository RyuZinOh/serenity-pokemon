import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from conviction.register import register_user   
from conviction.currency_related import show_vault
from conviction.poke_spawner import spawn_pokemon, dex_pokemon

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),intents=intents, case_insensitive=True)

@bot.event
async def on_ready():
    print(f"bot connected {bot.user}")

# passing all the failures for clean verboose
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass    
    else:
        raise error

            
#registering
bot.add_command(register_user)

#vault[currency related]
bot.add_command(show_vault)

#for spawning pokemon
bot.add_command(spawn_pokemon)


#dexing/viewing pokemon
bot.add_command(dex_pokemon)







bot.run(TOKEN)
