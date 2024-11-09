from config.connectDB import db_instance

#---------
# Checks if the user is registered in the database
#---------
async def is_user_registered(ctx):
    user_id = ctx.author.id
    users_collection = db_instance.get_users_collection()
    return users_collection.find_one({"user_id": user_id})

#---------
# Registers a new user in the database with initial values
#---------
async def register_user(ctx):
    user_id = ctx.author.id
    username = ctx.author.name
    join_date = str(ctx.author.joined_at.date()) 

    users_collection = db_instance.get_users_collection()

    if users_collection.find_one({"user_id": user_id}):
        await ctx.send("You are already registered.")
        return

    user_data = {
        "user_id": user_id,
        "username": username,
        "join_date": join_date,
        "status": True,  # User is active
        "serene": 0,     # Initializing serene currency to 0
        "spectra": 0,    # Initializing spectra currency to 0
        "redeems": 0     # Initializing redeems to 0
    }
    
    try:
        users_collection.insert_one(user_data)
        await ctx.send(f"Registration successful, {ctx.author.name}! 🎉")
    except Exception as e:
        await ctx.send(f"An error occurred during registration: {e}")
        print(f"Error registering user {user_id}: {e}")

#---------
# Retrieves the user's balance of serene and spectra
#---------
async def get_user_balance(ctx):
    user_id = ctx.author.id
    users_collection = db_instance.get_users_collection()
    
    user_data = users_collection.find_one({"user_id": user_id})
    if user_data:
        serene = user_data.get("serene", 0)
        spectra = user_data.get("spectra", 0)
        return serene, spectra
    return None, None  
