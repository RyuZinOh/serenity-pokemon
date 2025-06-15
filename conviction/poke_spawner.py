from utils.helper.checks import is_registered, is_poor
from utils.helper.decoraters import typing_effect
from discord.ext import commands
from datetime import datetime, timezone
import aiohttp
import random
import discord
import os
from dotenv import load_dotenv
from models.user_pokes import UserPokeModel
from models.currency import CurrencyModel
import json


load_dotenv()
OAURL = os.getenv("POKEMON_ART_URL")
P_A_B = os.getenv("POKEMON_API")
REGION = json.loads(os.getenv("GENERATION_REGION_MAP"))



p_m = UserPokeModel()
c_m = CurrencyModel()

@commands.command(name="spawn")
@is_registered()
@is_poor(500)
@typing_effect
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
                    "xp" : 0,
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



@commands.command(name="dex")
@is_registered()
@typing_effect
async def dex_pokemon(ctx, *, pokemon_name: str):
    try:
        pokemon_name = pokemon_name.lower()
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{P_A_B}/pokemon/{pokemon_name}") as resp:
                if resp.status != 200:
                    await ctx.send(f"{pokemon_name} doesn't exist! Explore more.")
                    return

                data = await resp.json()
                sprite_url = f"{OAURL}/{data['id']}.png"
                name = data["name"].capitalize()
                poke_id = data["id"]
                stats = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
                species_url = data["species"]["url"]

            async with session.get(species_url) as species_resp:
                if species_resp.status != 200:
                    await ctx.send("Failed to fetch species.")
                    return

                species = await species_resp.json()
                generation = species.get("generation",{}).get("name","unknown")
                region = REGION.get(generation,"Unknown region")
                katakana_name = next(
                    (n["name"] for n in species["names"] if n["language"]["name"] == "ja-Hrkt"),
                    "???"
                )
                description = next(
                    (entry["flavor_text"].replace("\n", " ").replace("\f", " ")
                     for entry in species["flavor_text_entries"]
                     if entry["language"]["name"] == "en"),
                    "No description."
                )

        embed = discord.Embed(
            title=f"{name} ⁜ {katakana_name}",
            description=description,
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=ctx.author.avatar.url)
        embed.set_image(url=sprite_url)
        embed.add_field(name="Region", value=region, inline=True)
        embed.add_field(name="Catchable", value="Yes", inline=True)
        embed.add_field(
            name="Base Stats",
            value="\n".join(f"**{y.replace('_', ' ').title()}:** {x}" for y, x in stats.items()),
            inline=False
        )
        embed.set_footer(text=f"Id:{poke_id}")
        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Error: {str(e)}")

                


                


