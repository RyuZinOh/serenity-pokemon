from utils.helper.checks import is_registered, is_poor
from discord.ext import commands
from datetime import datetime, timezone
import aiohttp
import random
import discord
import os
from dotenv import load_dotenv
from models.user_pokes import UserPokeModel
from models.currency import CurrencyModel

load_dotenv()
OAURL = os.getenv("POKEMON_ART_URL")
P_A_B = os.getenv("POKEMON_API")



p_m = UserPokeModel()
c_m = CurrencyModel()

@commands.command(name="spawn")
@is_registered()
@is_poor(500)
async def spawn_pokemon(ctx):
    try:
        async with aiohttp.ClientSession() as session:
            #get the pokemon limit
            async with session.get(f"{P_A_B}/pokemon-species?limit=1025") as resp:
                if resp.status !=200:
                    await ctx.send("Could not use the pokemon spawner at this time due to api connection issue")
                    return
                species_data  = await resp.json()
                total_pokemon = species_data["count"]


                pokemon_id  = random.randint(1, total_pokemon)


#actual spawning
            async with session.get(f"{P_A_B}/pokemon/{pokemon_id}") as resp:
                if resp.status !=200:
                    await ctx.send("Could not use the pokemon spawner at this time due to api connection issue")
                    return
                data = await resp.json()


                name = data["name"].capitalize()
                stats_raw = {stat["stat"]["name"]: stat["base_stat"] for stat in data["stats"]}
                image_url = f"{OAURL}/{pokemon_id}.png"

                def generate_iv():
                    return random.randint(0,31)

                cleaned_stats ={
                    "hp": generate_iv(),
                    "attack":generate_iv(),
                    "special_attack": generate_iv(),
                    "defense": generate_iv(),
                    "special_defense": generate_iv(),
                    "speed": generate_iv(),
                }

                pokemon_data = {
                    "name": name,
                    "level":1,
                    "stats" : cleaned_stats   
                }

                p_m.add_pokemon(str(ctx.author.id), pokemon_data)

                c_m.collection.update_one(
                    {"discord_id":str(ctx.author.id)},
                    {
                        "$inc":{"spectra_coin": -500},
                        "$set":{"last_updated": datetime.now(timezone.utc)}
                    }
                )

                await ctx.send(
                    f"{ctx.author.mention}!",
                    embed = create_pokemon_embed(ctx, name, image_url, cleaned_stats)
                )

    except Exception as e:
        await ctx.send(f"An unexpected error has occurred{str(e)}")




#creating embed to show user
def create_pokemon_embed(ctx,name, image_url, stats):
    embed = discord.Embed(
        title=f"you caught a {name}!",
        color=discord.Color.red()
    )
    stat_text = "\n".join(f"**{k.replace('_', ' ').title()}:** IV - {v}/31" for k, v in stats.items())
    embed.add_field(name="Stats" , value=stat_text, inline=False)
    embed.set_thumbnail(url=ctx.author.avatar.url)
    

    if image_url:
        embed.set_image(url=image_url)
    return embed




                


                


