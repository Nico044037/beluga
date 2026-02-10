import os
import discord
from discord.ext import commands
from datetime import datetime
import asyncio

# ================= BASIC CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")
MAIN_GUILD_ID = int(os.getenv("GUILD", "1452967364470505565"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=["!", "?", "$"],
    intents=intents,
    help_command=None
)

# ================= CONSTANTS =================
ALLOWED_USER = "nico044037"
TARGET_MENTION = "<@1419680644618780824>"

# ================= STORAGE =================
welcome_channel_id: int | None = None
autoroles: set[int] = set()
message_task: asyncio.Task | None = None

# ================= READY =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= RULES EMBED =================
def rules_embed():
    embed = discord.Embed(
        title="📜 Server Rules",
        color=discord.Color.red()
    )
    embed.add_field(
        name="Rules",
        value=(
            "🤝 Be respectful\n"
            "🚫 No spamming\n"
            "🔞 No NSFW\n"
            "📢 No advertising\n"
            "👮 Staff decisions are final"
        ),
        inline=False
    )
    return embed

# ================= SETUP =================
@bot.command()
@commands.has_permissions(manage_guild=True)
async def setup(ctx, channel: discord.TextChannel):
    if ctx.guild.id != MAIN_GUILD_ID:
        return
    global welcome_channel_id
    welcome_channel_id = channel.id
    await ctx.send(f"✅ Welcome channel set to {channel.mention}")

# ================= SEND RULES =================
@bot.command()
async def send(ctx):
    await ctx.send(embed=rules_embed())

# ================= AUTOROLE =================
@bot.command()
@commands.has_permissions(manage_roles=True)
async def autorole(ctx, action: str, role: discord.Role):
    if action.lower() == "add":
        autoroles.add(role.id)
        await ctx.send(f"✅ Added {role.mention}")
    elif action.lower() == "remove":
        autoroles.discard(role.id)
        await ctx.send(f"❌ Removed {role.mention}")

# ================= MEMBER JOIN =================
@bot.event
async def on_member_join(member: discord.Member):
    if member.guild.id != MAIN_GUILD_ID:
        return
    for role_id in autoroles:
        role = member.guild.get_role(role_id)
        if role:
            await member.add_roles(role)

# ================= MESSAGE TASK =================
async def spam_message(channel: discord.TextChannel):
    try:
        while True:
            await channel.send(TARGET_MENTION)
    except asyncio.CancelledError:
        pass

# ================= SUDO GROUP =================
@bot.group(name="sudo", invoke_without_command=True)
async def sudo(ctx):
    await ctx.send("❌ Usage: `$sudo <command>`")

# ================= START MESSAGE =================
@sudo.command(name="startmessage")
async def sudo_startmessage(ctx):
    global message_task

    if ctx.author.name != ALLOWED_USER:
        await ctx.send("❌ Access denied")
        return

    if message_task and not message_task.done():
        await ctx.send("❌ Already running")
        return

    message_task = asyncio.create_task(spam_message(ctx.channel))
    await ctx.send("✅ Message spam started")

# ================= STOP MESSAGE =================
@sudo.command(name="stopmessage")
async def sudo_stopmessage(ctx):
    global message_task

    if ctx.author.name != ALLOWED_USER:
        await ctx.send("❌ Access denied")
        return

    if not message_task:
        await ctx.send("❌ No active task")
        return

    message_task.cancel()
    message_task = None
    await ctx.send("🛑 Message spam stopped")

# ================= ERROR HANDLER =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Error: {error}")

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

bot.run(TOKEN)

