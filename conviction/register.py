from datetime import datetime, timezone
from models.user import UserModel

u_model = UserModel()
async def register_user(ctx):
    disc_id = ctx.author.id
    username = ctx.author.name

    if u_model.user_exists(disc_id):
        await ctx.send("Already registered")
        return
    else:
        u_model.create_user(disc_id, username)
        await ctx.send(f"{username}, you have been successfully registered")