import os
import discord
from discord.ext import commands
from datetime import datetime
from urllib.parse import urlencode

# ================= CONFIG =================
TOKEN = os.getenv("DISCORD_TOKEN")

OWNER_USERNAME = "nico044037"
CLIENT_ID = os.getenv("CLIENT_ID")  # put your bot's CLIENT ID in Railway

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=["$", "!", "?"],
    intents=intents,
    help_command=None
)

# ================= READY =================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# ================= OWNER CHECK =================
def owner_only(ctx):
    return ctx.author.name == OWNER_USERNAME

# ================= SUDO GROUP =================
@bot.group(name="sudo", invoke_without_command=True)
async def sudo(ctx):
    await ctx.send("❌ usage: `$sudo askjoin | members`")

# ================= ASK TO JOIN =================
@sudo.command(name="askjoin")
async def sudo_askjoin(ctx):
    if not owner_only(ctx):
        await ctx.send("❌ access denied")
        return

    if not CLIENT_ID:
        await ctx.send("❌ CLIENT_ID not set")
        return

    params = {
        "client_id": CLIENT_ID,
        "scope": "bot applications.commands",
        "permissions": "0",
        "response_type": "code",
        "integration_type": "0"
    }

    oauth_url = "https://discord.com/oauth2/authorize?" + urlencode(params)

    embed = discord.Embed(
        title="🔐 Request Bot Join",
        description=(
            "Click the button below.\n\n"
            "Discord will ask you to approve which **servers you manage** "
            "this bot can join."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="How it works",
        value="Bot asks → You approve → Bot joins",
        inline=False
    )

    await ctx.send(embed=embed)
    await ctx.send(oauth_url)

# ================= MEMBERS =================
@sudo.command(name="members")
async def sudo_members(ctx):
    if not owner_only(ctx):
        await ctx.send("❌ access denied")
        return

    guild = ctx.guild
    humans = len([m for m in guild.members if not m.bot])
    bots = len([m for m in guild.members if m.bot])

    embed = discord.Embed(
        title="👥 Member Count",
        color=discord.Color.green(),
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="Server", value=guild.name, inline=False)
    embed.add_field(name="Total", value=guild.member_count, inline=True)
    embed.add_field(name="Humans", value=humans, inline=True)
    embed.add_field(name="Bots", value=bots, inline=True)

    await ctx.send(embed=embed)

# ================= ERROR HANDLER =================
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ error: {error}")

# ================= START =================
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN environment variable not set")

bot.run(TOKEN)
