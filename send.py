import os
import asyncio
import discord
from discord.ext import commands

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_USERNAME = "nico044037"
SPAM_MESSAGE = "<@1419680644618780824>"
SPAM_DELAY = 0.8  # SAFE delay (do NOT go lower)

intents = discord.Intents.default()
intents.message_content = True  # REQUIRED for prefix commands

bot = commands.Bot(
    command_prefix=["$", "!", "?"],
    intents=intents,
    help_command=None
)

spam_task: asyncio.Task | None = None

# ================= READY =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= OWNER CHECK =================
def owner_only(ctx):
    return ctx.author.name == OWNER_USERNAME

# ================= SPAM LOOP =================
async def spam_loop(channel: discord.abc.Messageable):
    try:
        while True:
            await channel.send(SPAM_MESSAGE)
            await asyncio.sleep(SPAM_DELAY)
    except asyncio.CancelledError:
        pass
    except discord.Forbidden:
        pass

# ================= SUDO GROUP =================
@bot.group(name="sudo", invoke_without_command=True)
async def sudo(ctx):
    if not owner_only(ctx):
        return
    await ctx.send("Commands: `$sudo startmessage` `$sudo stopmessage`")

# ================= START MESSAGE =================
@sudo.command(name="startmessage")
async def sudo_startmessage(ctx):
    global spam_task

    if not owner_only(ctx):
        return

    if spam_task and not spam_task.done():
        await ctx.send("❌ already running")
        return

    spam_task = asyncio.create_task(spam_loop(ctx.channel))
    await ctx.send("✅ spam started")

# ================= STOP MESSAGE =================
@sudo.command(name="stopmessage")
async def sudo_stopmessage(ctx):
    global spam_task

    if not owner_only(ctx):
        return

    if not spam_task:
        await ctx.send("❌ no active spam")
        return

    spam_task.cancel()
    spam_task = None
    await ctx.send("🛑 spam stopped")

# ================= ERROR HANDLER =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send("❌ error")

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

bot.run(TOKEN)
