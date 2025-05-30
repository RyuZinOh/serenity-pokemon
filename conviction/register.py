from models.user import UserModel
from models.currency import CurrencyModel
from discord.ext import commands
from models.user_pokes import UserPokeModel

u_model = UserModel()
vault = CurrencyModel()
u_ps = UserPokeModel()

@commands.command(name="register")
async def register_user(ctx):
    disc_id = ctx.author.id
    username = ctx.author.name

    if u_model.user_exists(disc_id):
        await ctx.send("Already registered")
        return
    else:
        u_model.create_user(disc_id, username)
        vault.create_vault(disc_id)
        u_ps.create_user_pokes(disc_id)
        await ctx.send(f"{username}, you have been successfully registered")