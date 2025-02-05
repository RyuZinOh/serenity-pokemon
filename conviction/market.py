import math
import requests
import discord
from config.connectDB import db_instance
from discord.ui import Select, View, Button
import os

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




# ##store section
# //fetching datas
def fetch_titles_data():
    titles_api_url = os.getenv("TITLES_API")
    if not titles_api_url:
        raise ValueError("TITLES_API environment variable is not set.")
    response = requests.get(titles_api_url)
    return response.json() if response.status_code == 200 else None

def fetch_definition_data():
    definition_api_url = os.getenv("DEFINITION_API")
    if not definition_api_url:
        raise ValueError("DEFINITION_API environment variable is not set.")
    response = requests.get(definition_api_url)
    return response.json() if response.status_code == 200 else None

def fetch_backgrounds_data():
    data = fetch_definition_data()
    return data.get('backgrounds', None) if data else None

def fetch_cards_data():
    data = fetch_definition_data()
    return data.get('cards', None) if data else None

#main 
class StoreDropdown(discord.ui.Select):
    def __init__(self, ctx):
        self.ctx = ctx
        options = [
            discord.SelectOption(label="Background", description="Browse backgrounds."),
            discord.SelectOption(label="Cards", description="View unique cards."),
            discord.SelectOption(label="Titles", description="Explore custom titles.")
        ]
        super().__init__(placeholder="Select a category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Titles":
            titles_data = fetch_titles_data()
            if titles_data:
                await show_titles_page(interaction, titles_data, page=1)
            else:
                await interaction.response.send_message("Failed to load titles data.", ephemeral=True)
        elif self.values[0] == "Background":
            backgrounds_data = fetch_backgrounds_data()
            if backgrounds_data:
                await show_backgrounds_page(interaction, backgrounds_data, page=1)
            else:
                await interaction.response.send_message("Failed to load backgrounds data.", ephemeral=True)
        elif self.values[0] == "Cards":
            cards_data = fetch_cards_data()
            if cards_data:
                await show_cards_page(interaction, cards_data, page=1)
            else:
                await interaction.response.send_message("Failed to load cards data.", ephemeral=True)

async def view_other_store(ctx):
    view = discord.ui.View()
    view.add_item(StoreDropdown(ctx))
    embed = discord.Embed(
        title="Exclusive Store",
        description="Explore premium selections below!",
        color=discord.Color.purple()
    )
    embed.set_image(url="attachment://store_banner.png")
    embed.set_footer(text="Select a category from the dropdown to proceed.")
    await ctx.send(embed=embed, file=discord.File("assets/dash_shop.png", filename="store_banner.png"), view=view)

#titles
async def show_titles_page(interaction, titles_data, page):
    per_page = 10
    total_pages = math.ceil(len(titles_data) / per_page)
    start, end = (page - 1) * per_page, page * per_page
    title_items = list(titles_data.items())[start:end]

    embed = discord.Embed(
        title=f"Titles Store (Page {page}/{total_pages})",
        color=discord.Color.blue()
    )
    embed.description = "Browse available titles and select one from the dropdown."

    for title_id, (name, price) in title_items:
        embed.add_field(name=f"**{name}**", value=f"`ID: {title_id}` | `{price} Spectra`", inline=False)

    view = discord.ui.View()
    view.add_item(TitlesPageDropdown(titles_data, page, total_pages))

    if page > 1:
        view.add_item(PageButton("◀️", titles_data, page - 1, "Titles"))
    if page < total_pages:
        view.add_item(PageButton("▶️", titles_data, page + 1, "Titles"))

    await interaction.response.edit_message(embed=embed, view=view)

class TitlesPageDropdown(discord.ui.Select):
    def __init__(self, titles_data, page, total_pages):
        per_page = 10
        start, end = (page - 1) * per_page, page * per_page
        options = [
            discord.SelectOption(label=name, description=f"Price: {price} Spectra")
            for _, (name, price) in list(titles_data.items())[start:end]
        ]
        super().__init__(placeholder="Select a title...", options=options)
        self.titles_data = titles_data

    async def callback(self, interaction: discord.Interaction):
        selected_title = self.values[0]
        price = next(price for _, (name, price) in self.titles_data.items() if name == selected_title)
        await interaction.response.send_message(f"**Title:** {selected_title}\n**Price:** {price} Spectra", ephemeral=True)

class PageButton(discord.ui.Button):
    def __init__(self, emoji, data, new_page, category):
        super().__init__(style=discord.ButtonStyle.primary, emoji=emoji)
        self.data = data
        self.new_page = new_page
        self.category = category

    async def callback(self, interaction: discord.Interaction):
        if self.category == "Titles":
            await show_titles_page(interaction, self.data, self.new_page)
        elif self.category == "Backgrounds":
            await show_backgrounds_page(interaction, self.data, self.new_page)
        elif self.category == "Cards":
            await show_cards_page(interaction, self.data, self.new_page)

#backgrounds
async def show_backgrounds_page(interaction, backgrounds_data, page):
    per_page = 10
    total_pages = math.ceil(len(backgrounds_data) / per_page)
    start, end = (page - 1) * per_page, page * per_page
    background_items = list(backgrounds_data.items())[start:end]

    embed = discord.Embed(
        title=f"Backgrounds Store (Page {page}/{total_pages})",
        color=discord.Color.green()
    )
    embed.description = "Browse available backgrounds and select one from the dropdown."

    for filename, (description, price) in background_items:
        embed.add_field(name=f"**{description}**", value=f"`File: {filename}` | `{price} Spectra`", inline=False)

    view = discord.ui.View()
    view.add_item(BackgroundsPageDropdown(backgrounds_data, page, total_pages))

    if page > 1:
        view.add_item(PageButton("◀️", backgrounds_data, page - 1, "Backgrounds"))
    if page < total_pages:
        view.add_item(PageButton("▶️", backgrounds_data, page + 1, "Backgrounds"))

    await interaction.response.edit_message(embed=embed, view=view)

class BackgroundsPageDropdown(discord.ui.Select):
    def __init__(self, backgrounds_data, page, total_pages):
        per_page = 10
        start, end = (page - 1) * per_page, page * per_page
        options = [
            discord.SelectOption(label=description, description=f"Price: {price} Spectra")
            for _, (description, price) in list(backgrounds_data.items())[start:end]
        ]
        super().__init__(placeholder="Select a background...", options=options)
        self.backgrounds_data = backgrounds_data

    async def callback(self, interaction: discord.Interaction):
        selected_background = self.values[0]
        price = next(price for _, (description, price) in self.backgrounds_data.items() if description == selected_background)
        await interaction.response.send_message(f"**Background:** {selected_background}\n**Price:** {price} Spectra", ephemeral=True)

#cards
async def show_cards_page(interaction, cards_data, page):
    per_page = 10
    total_pages = math.ceil(len(cards_data) / per_page)
    start, end = (page - 1) * per_page, page * per_page
    card_items = list(cards_data.items())[start:end]

    embed = discord.Embed(
        title=f"Cards Store (Page {page}/{total_pages})",
        color=discord.Color.red()
    )
    embed.description = "Browse available cards and select one from the dropdown."

    for filename, (description, price) in card_items:
        embed.add_field(name=f"**{description}**", value=f"`File: {filename}` | `{price} Spectra`", inline=False)

    view = discord.ui.View()
    view.add_item(CardsPageDropdown(cards_data, page, total_pages))

    if page > 1:
        view.add_item(PageButton("◀️", cards_data, page - 1, "Cards"))
    if page < total_pages:
        view.add_item(PageButton("▶️", cards_data, page + 1, "Cards"))

    await interaction.response.edit_message(embed=embed, view=view)

class CardsPageDropdown(discord.ui.Select):
    def __init__(self, cards_data, page, total_pages):
        per_page = 10
        start, end = (page - 1) * per_page, page * per_page
        options = [
            discord.SelectOption(label=description, description=f"Price: {price} Spectra")
            for _, (description, price) in list(cards_data.items())[start:end]
        ]
        super().__init__(placeholder="Select a card...", options=options)
        self.cards_data = cards_data

    async def callback(self, interaction: discord.Interaction):
        selected_card = self.values[0]
        price = next(price for _, (description, price) in self.cards_data.items() if description == selected_card)
        await interaction.response.send_message(f"**Card:** {selected_card}\n**Price:** {price} Spectra", ephemeral=True)
