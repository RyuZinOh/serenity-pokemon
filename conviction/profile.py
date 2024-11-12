import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import requests
from config.connectDB import db_instance

async def generate_profile(ctx):
    user_id = ctx.author.id
    users_collection = db_instance.get_users_collection()
    banners_collection = db_instance.get_banners_collection()  
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data:
        await ctx.send("You need to register first using the `!register` command.")
        return

    # Retrieve the default banner (11.jpg)
    default_banner_data = banners_collection.find_one({"path": {"$regex": "11.jpg"}})
    if not default_banner_data:
        await ctx.send("Default banner not found.")
        return

    # Use the path directly from the banner data
    default_banner_path = default_banner_data["path"]
    banner = Image.open(default_banner_path)  
    banner = banner.resize((1440, 552))  

    # Set up profile image
    username = ctx.author.name
    join_date = str(ctx.author.joined_at.date())
    inventory = user_data.get("inventory", [])
    pokemon_count = len(inventory)
    width, height = 1440, 920

    # Base Image
    img = Image.new("RGB", (width, height), color="white")
    img.paste(banner, (0, 0))

    # User's Avatar
    avatar_url = str(ctx.author.avatar.url)
    response = requests.get(avatar_url)
    avatar = Image.open(io.BytesIO(response.content)).resize((250, 250)).convert("RGBA")
    mask = Image.new("L", (250, 250), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 250, 250), fill=255)
    avatar.putalpha(mask)
    avatar_top_y = 552 - 125
    img.paste(avatar, (50, avatar_top_y), avatar)

    # Font setup
    font_big = ImageFont.truetype("arial.ttf", 50)
    font_small = ImageFont.truetype("arial.ttf", 30)
    text_x_offset = 50 
    text_y_offset = avatar_top_y +250

    # Draw Username, Pokémon Count
    draw = ImageDraw.Draw(img)
    draw.text((text_x_offset, text_y_offset), f"{username}", font=font_big, fill="black")
    draw.text((text_x_offset, text_y_offset + 70), f"Pokémon Caught: {pokemon_count}", font=font_small, fill="black")

    # Draw Join Date
    font_date = ImageFont.truetype("arial.ttf", 20)
    date_x_offset = width - 300
    date_y_offset = height - 50
    draw.text((date_x_offset, date_y_offset), f"Account Created: {join_date}", font=font_date, fill="black")

    # Save to BytesIO for Discord upload
    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0) 
        file = discord.File(image_binary, filename="profile.png")
        return file
