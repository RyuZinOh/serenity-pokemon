import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from utils.helper.checks import is_registered
from conviction.register import register_user     

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),intents=intents, case_insensitive=True)


# passing all the failures for clean verboose
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        pass    
    else:
        raise error


@bot.command(name="register")
async def register(ctx):
    try:
        await register_user(ctx)
    except Exception as e:
        await ctx.send(f"An error occured during registration: {e}")
            


# testing the checker
@bot.command(name="test")
@is_registered()
async def check_me(ctx):
    await ctx.send(f"{ctx.author.name}, you are registered!")





bot.run(TOKEN)
