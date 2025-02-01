import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from conviction.register import register_user, is_user_registered, get_user_balance
from conviction.pokeDex import fetch_pokemon_data
from config.pokemonView import create_pokemon_embed
from conviction.market import create_market_embed, buy_redeem, view_redeem, view_other_store
from config.connectDB import db_instance
from config.usercontrol import redeem, catch, p, info
import random
from conviction.profile import generate_profile



load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents, case_insensitive=True)

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
        embed.add_field(name="Serene", value=f"{serene}", inline=True)
        embed.add_field(name="Spectra", value=f"{spectra}", inline=True)
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
    if item == "redeem":
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

@bot.command()
async def profile(ctx):
    profile_image = await generate_profile(ctx)
    if profile_image:
        await ctx.send(file=profile_image)


@bot.command(name="store")
async def store(ctx):
    try:
        await view_other_store(ctx)
    except Exception as e:
        await ctx.send(f"An error occurred while opening the store: {e}")
        print(f"Error opening store: {e}")



        

bot.run(TOKEN)
