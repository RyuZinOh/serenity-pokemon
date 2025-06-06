from discord.ext import commands
from models.currency import CurrencyModel
from utils.helper.checks import is_registered
from discord import Embed
import discord
from utils.helper.decoraters import typing_effect

vault = CurrencyModel()

@commands.command(name="vault")
@is_registered()
@typing_effect
async def show_vault(ctx):
    disc_id = str(ctx.author.id)
    user_data = vault.collection.find_one({"discord_id":disc_id})

    if user_data:
        spectra = user_data.get("spectra_coin")
        sera   = user_data.get("sera_token")

        embed = Embed(
            color= discord.Color.red()
        )
        embed.add_field(name="Spectra Coin", value=f"{spectra}", inline=False)
        embed.add_field(name="Sera Token", value=f"{sera}", inline=False)

        embed.set_thumbnail(url=ctx.author.avatar.url)



        await ctx.send(
            embed= embed
        )
    else:
        await ctx.send("User Vault not found. You might want to register.")    