import os
import asyncio
import discord
from discord.ext import commands

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")
OWNER_ID = 1258115928525373570

ANNOUNCE_DELAY = 10  # seconds (safe, adjustable)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=["$", "!", "?"],
    intents=intents,
    help_command=None
)

announce_task: asyncio.Task | None = None

# ================= READY =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= OWNER CHECK =================
def is_owner(ctx: commands.Context) -> bool:
    return ctx.author.id == OWNER_ID

# ================= ANNOUNCE LOOP =================
async def announce_loop(channel: discord.TextChannel, message: str):
    try:
        while True:
            await channel.send(message)
            await asyncio.sleep(ANNOUNCE_DELAY)
    except asyncio.CancelledError:
        pass

# ================= SUDO GROUP =================
@bot.group(name="sudo", invoke_without_command=True)
async def sudo(ctx):
    if not is_owner(ctx):
        return
    await ctx.send(
        "Commands:\n"
        "`$sudo announce <message>`\n"
        "`$sudo stop`"
    )

# ================= START ANNOUNCE =================
@sudo.command(name="announce")
async def sudo_announce(ctx, *, message: str):
    global announce_task

    if not is_owner(ctx):
        return

    if announce_task and not announce_task.done():
        await ctx.send("❌ announcement already running")
        return

    announce_task = asyncio.create_task(
        announce_loop(ctx.channel, message)
    )
    await ctx.send("✅ announcement started")

# ================= STOP ANNOUNCE =================
@sudo.command(name="stop")
async def sudo_stop(ctx):
    global announce_task

    if not is_owner(ctx):
        return

    if not announce_task:
        await ctx.send("❌ no active announcement")
        return

    announce_task.cancel()
    announce_task = None
    await ctx.send("🛑 announcement stopped")

# ================= ERROR HANDLER =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error  # don’t hide real bugs while developing

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

bot.run(TOKEN)
