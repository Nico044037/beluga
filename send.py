import os
import asyncio
import discord
from discord.ext import commands

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")

AUTHORIZED_USERNAME = "nico044037"
SPAM_MESSAGE = "<@1419680644618780824>"
SPAM_DELAY = 0.1  # seconds

# IMPORTANT: NO privileged intents
intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix=["$", "!", "?"],
    intents=intents,
    help_command=None
)

# user_id -> asyncio.Task
spam_tasks: dict[int, asyncio.Task] = {}

# ================= READY =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= PERMISSION CHECK =================
def is_authorized(ctx):
    return ctx.author.name == AUTHORIZED_USERNAME

# ================= SPAM LOOP =================
async def spam_loop(user: discord.User):
    try:
        while True:
            await user.send(SPAM_MESSAGE)
            await asyncio.sleep(SPAM_DELAY)
    except asyncio.CancelledError:
        pass
    except discord.Forbidden:
        pass

# ================= SUDO GROUP =================
@bot.group(name="sudo", invoke_without_command=True)
async def sudo(ctx):
    if not is_authorized(ctx):
        return
    await ctx.send("Available: `$sudo startmessage <user_id>` `$sudo stopmessage <user_id>`")

# ================= START MESSAGE =================
@sudo.command(name="startmessage")
async def sudo_startmessage(ctx, user_id: int):
    if not is_authorized(ctx):
        return

    if user_id in spam_tasks:
        await ctx.send("❌ already running")
        return

    try:
        user = await bot.fetch_user(user_id)
    except:
        await ctx.send("❌ invalid user")
        return

    task = asyncio.create_task(spam_loop(user))
    spam_tasks[user_id] = task

    await ctx.send(f"✅ started spam for `{user}`")

# ================= STOP MESSAGE =================
@sudo.command(name="stopmessage")
async def sudo_stopmessage(ctx, user_id: int):
    if not is_authorized(ctx):
        return

    task = spam_tasks.get(user_id)
    if not task:
        await ctx.send("❌ no active spam")
        return

    task.cancel()
    spam_tasks.pop(user_id, None)

    await ctx.send(f"✅ stopped spam for `{user_id}`")

# ================= ERROR HANDLER =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ invalid arguments")
    else:
        await ctx.send("❌ error")
        raise error

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

bot.run(TOKEN)
