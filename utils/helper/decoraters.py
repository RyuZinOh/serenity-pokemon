from functools import wraps

def typing_effect(func):
    @wraps(func)
    async def wrapper(ctx, *args,**kwargs):
        async with ctx.typing():
            return  await func(ctx, *args, **kwargs)    
    return wrapper