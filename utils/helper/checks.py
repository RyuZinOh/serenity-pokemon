from discord.ext import commands
from models.user import UserModel

u_model = UserModel()

def is_registered():
    async def predicate(ctx):
        if not u_model.user_exists(ctx.author.id):
            await ctx.send("You must be registered!!, try registereing with `register` command first.")
            return False
        return True
    return commands.check(predicate)




