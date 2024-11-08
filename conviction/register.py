from config.connnectDB import connect_mongo
users_collection = connect_mongo()

async def register_user(ctx):
    user_id = ctx.author.id
    username = ctx.author.name
    join_date = str(ctx.author.joined_at.date()) 

    if users_collection.find_one({"user_id": user_id}):
        await ctx.send("You are already registered.")
        return

    user_data = {
        "user_id": user_id,
        "username": username,
        "join_date": join_date,
        "status": True 
    }
    
    try:
        users_collection.insert_one(user_data)
        await ctx.send(f"Registration successful, {ctx.author.name}! 🎉")
    except Exception as e:
        await ctx.send(f"An error occurred during registration: {e}")
        print(f"Error registering user {user_id}: {e}")
