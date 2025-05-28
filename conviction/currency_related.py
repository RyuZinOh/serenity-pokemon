from discord.ext import commands
from models.currency import CurrencyModel
from utils.helper.checks import is_registered

vault = CurrencyModel()

@commands.command(name="vault")
@is_registered()
async def show_vault(ctx):
    disc_id = str(ctx.author.id)
    user_data = vault.collection.find_one({"discord_id":disc_id})

    if user_data:
        spectra = user_data.get("spectra_coin")
        sera   = user_data.get("sera_token")
        await ctx.send(
            f"{ctx.author.name}-> Spectra coin: {spectra}-> Sera Token:{sera}"
        )
    else:
        await ctx.send("User Vault not found. You might want to register.")    