import discord
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import requests
from config.connectDB import db_instance

async def generate_profile(ctx):
    user_id = ctx.author.id
    users_collection = db_instance.get_users_collection()
    user_data = users_collection.find_one({"user_id": user_id})

    if not user_data:
        await ctx.send("You need to register first using the `!register` command.")
        return

    username = ctx.author.name
    join_date = str(ctx.author.joined_at.date())

    inventory = user_data.get("inventory", [])
    pokemon_count = len(inventory)

    width, height = 1440, 920
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    banner_height = 500
    draw.rectangle([0, 0, width, banner_height], fill=(0, 123, 255))

    avatar_url = str(ctx.author.avatar.url)
    response = requests.get(avatar_url)
    avatar = Image.open(io.BytesIO(response.content))
    avatar = avatar.resize((250, 250))
    avatar = ImageOps.fit(avatar, (250, 250), method=0, bleed=0.0, centering=(0.5, 0.5))
    avatar = avatar.convert("RGBA")

    mask = Image.new("L", (250, 250), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, 250, 250), fill=255)

    avatar.putalpha(mask)

    avatar_top_y = int(banner_height - 125)
    avatar_left_x = 50
    img.paste(avatar, (avatar_left_x, avatar_top_y), avatar)

    font_big = ImageFont.truetype("arial.ttf", 50)
    font_small = ImageFont.truetype("arial.ttf", 30)

    text_x_offset = avatar_left_x 
    text_y_offset = avatar_top_y + 250 

    draw.text((text_x_offset, text_y_offset), f"{username}", font=font_big, fill="black")
    text_y_offset += 70

    draw.text((text_x_offset, text_y_offset), f"Pokémon Caught: {pokemon_count}", font=font_small, fill="black")

    font_date = ImageFont.truetype("arial.ttf", 20)
    date_x_offset = width - 300
    date_y_offset = height - 50
    draw.text((date_x_offset, date_y_offset), f"Account Created: {join_date}", font=font_date, fill="black")

    with io.BytesIO() as image_binary:
        img.save(image_binary, "PNG")
        image_binary.seek(0)
        file = discord.File(image_binary, filename="profile.png")
        return file
