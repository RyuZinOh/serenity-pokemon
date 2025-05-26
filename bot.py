import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from conviction.register import register_user     

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"),intents=intents, case_insensitive=True)




@bot.command(name="register")
async def register(ctx):
    try:
        await register_user(ctx)
    except Exception as e:
        await ctx.send(f"An error occured during registration: {e}")
            





bot.run(TOKEN)
