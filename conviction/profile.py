import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import requests
import json
from config.connectDB import db_instance


async def generate_profile(ctx):
    user_id = ctx.author.id
    user_data = db_instance.get_users_collection().find_one({"user_id": user_id})

    if not user_data:
        await ctx.send("You need to register first using the `!register` command.")
        return

    # Fetch metadata JSON from GitHub
    metadata_url = "https://raw.githubusercontent.com/RyuZinOh/static-assets/main/metadata.json"
    try:
        metadata_response = requests.get(metadata_url, timeout=10)
        metadata_response.raise_for_status()
        metadata = metadata_response.json()
        backgrounds = metadata.get("backgrounds", [])
    except (requests.RequestException, json.JSONDecodeError) as e:
        await ctx.send("Failed to fetch metadata. Please try again later.")
        return

    # 11 be the default erenityProfiles banner
    banner_id = 11  
    banner_filename = next((bg for bg in backgrounds if bg.startswith(f"{banner_id}.")), None)

    if not banner_filename:
        await ctx.send(f"No background found for ID {banner_id}.")
        return

    # Fetch the banner
    github_repo_url = "https://raw.githubusercontent.com/RyuZinOh/static-assets/main/Backgrounds/"
    banner_url = f"{github_repo_url}{banner_filename}"
    try:
        banner_response = requests.get(banner_url, timeout=10)
        banner_response.raise_for_status()
        banner = Image.open(io.BytesIO(banner_response.content)).resize((1440, 552))
    except requests.RequestException as e:
        await ctx.send("Failed to load the banner. Please try again later.")
        return

    # User avatar
    avatar_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
    try:
        avatar_response = requests.get(avatar_url, timeout=10)
        avatar_response.raise_for_status()
        avatar = Image.open(io.BytesIO(avatar_response.content)).resize((250, 250)).convert("RGBA")
    except requests.RequestException as e:
        await ctx.send("Failed to load the avatar. Please try again later.")
        return

    # Create the profile image
    img = Image.new("RGB", (1440, 920), "white")
    img.paste(banner, (0, 0))
    mask = Image.new("L", (250, 250), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, 250, 250), fill=255)
    avatar.putalpha(mask)
    img.paste(avatar, (50, 552 - 125), avatar)

    draw = ImageDraw.Draw(img)
    try:
        font_big = ImageFont.truetype("arial.ttf", 50)
        font_small = ImageFont.truetype("arial.ttf", 30)
        font_date = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        await ctx.send("Font file missing. Contact the administrator.")
        return

    username = ctx.author.name
    pokemon_count = len(user_data.get("inventory", []))
    join_date = str(ctx.author.joined_at.date())

    draw.text((50, 552 + 125), username, font=font_big, fill="black")
    draw.text((50, 552 + 200), f"Pokémon Caught: {pokemon_count}", font=font_small, fill="black")
    draw.text((1440 - 300, 920 - 50), f"Account Created: {join_date}", font=font_date, fill="black")

    # Save to BytesIO for Discord upload
    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(fp=image_binary, filename="profile.png")
        return file
