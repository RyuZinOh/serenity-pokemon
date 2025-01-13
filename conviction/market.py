import discord
from config.connectDB import db_instance

#---------
# Creates the market embed to display available items and their costs
#---------
def create_market_embed():
    items = {
        "Redeem": "20,000 Spectra Coins",
        "Incense": "5,000 Serene Coins"
    }

    embed = discord.Embed(
        title="Marketplace",
        description="Explore our offerings below. Select your items with ease!",
        color=discord.Color.gold()
    )

    for item, price in items.items():
        embed.add_field(name=item, value=f"Price: {price}", inline=False)

    embed.set_footer(text="Use the respective commands to complete your purchase.")
    
    return embed



#---------
# Constants for Redeem purchase logic and limits
#---------
REDEEM_COST = 20000
MAX_REDEEM_PURCHASE = 5

#---------
# Handles the process of buying Redeems from the market
#---------
async def buy_redeem(ctx, amount=1):
    if amount < 1 or amount > MAX_REDEEM_PURCHASE:
        await ctx.send(f"You can only buy between 1 and {MAX_REDEEM_PURCHASE} Redeems at a time.")
        return

    user_id = ctx.author.id
    users_collection = db_instance.get_users_collection()
    user_data = users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        await ctx.send("You need to register first using the `!register` command.")
        return

    total_cost = REDEEM_COST * amount
    current_spectra = user_data.get("spectra", 0)
    
    if current_spectra < total_cost:
        await ctx.send(f"You don't have enough Spectra coins. You need {total_cost} Spectra coins.")
        return

    new_spectra = current_spectra - total_cost
    new_redeems = user_data.get("redeems", 0) + amount

    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"spectra": new_spectra, "redeems": new_redeems}}
    )

    await ctx.send(f"Successfully bought {amount} Redeem(s)! Your new balance: {new_spectra} Spectra coins, {new_redeems} Redeem(s).")

#---------
# Displays the current Redeem count for the user
#---------
async def view_redeem(ctx):
    user_id = ctx.author.id
    users_collection = db_instance.get_users_collection()
    
    user_data = users_collection.find_one({"user_id": user_id})
    
    if not user_data:
        await ctx.send("You need to register first using the `!register` command.")
        return
    
    redeems = user_data.get("redeems", 0)
    
    embed = discord.Embed(
        title=f"{ctx.author.name}",
        description=f"**Redeem**\n**{redeems}**\n",
        color=discord.Color.blue()
    )
    
    embed.set_thumbnail(url=ctx.author.avatar.url)
    embed.set_footer(text="- Serving you the best!", icon_url=ctx.author.avatar.url)

    await ctx.send(embed=embed)
