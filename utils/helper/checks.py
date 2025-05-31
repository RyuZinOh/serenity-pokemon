from discord.ext import commands
from models.user import UserModel
from models.currency import CurrencyModel
c_model = CurrencyModel()
u_model = UserModel()
import asyncio

def is_registered():
    async def predicate(ctx):
        if not u_model.user_exists(ctx.author.id):
            await ctx.send("You must be registered!!, try registereing with `register` command first.")
            return False
        return True
    return commands.check(predicate)


#check user poor or not
def is_poor(required_spectra):
    async def predicate(ctx):
        loop = asyncio.get_event_loop()
        user = await loop.run_in_executor(
            None,
            lambda : c_model.collection.find_one({"discord_id": str(ctx.author.id)})
        )

        if not user or user.get("spectra_coin") < required_spectra:
            await ctx.send("you are poor! Earn some spectra coins from anything we offer.")
            return False
        
        return True
    
    return commands.check(predicate)
