import os
import discord
from discord.ext import commands

# Get token from Railway environment variable
TOKEN = os.getenv("TOKEN")

# Intents (VERY IMPORTANT)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("Anti-ping system is active.")

@bot.event
async def on_message(message: discord.Message):
    # Ignore bots
    if message.author.bot:
        return

    # Ignore DMs
    if message.guild is None:
        return

    guild = message.guild

    # Fetch owner reliably (fixes Railway/cache issues)
    try:
        owner = guild.owner or await guild.fetch_member(guild.owner_id)
    except:
        owner = None

    # OWNER BYPASS (owner can ping and use @everyone/@here)
    if owner and message.author.id == owner.id:
        await bot.process_commands(message)
        return

    # --- BLOCK @everyone AND @here ---
    if message.mention_everyone:
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, you are NOT allowed to ping everyone or here.",
                delete_after=5
            )
        except discord.Forbidden:
            print("Missing Manage Messages permission.")
        except discord.HTTPException:
            pass
        return

    # --- BLOCK PINGING THE SERVER OWNER ---
    if owner:
        for user in message.mentions:
            if user.id == owner.id:
                try:
                    await message.delete()
                    await message.channel.send(
                        f"{message.author.mention}, you cannot ping the server owner.",
                        delete_after=5
                    )
                except discord.Forbidden:
                    print("Missing Manage Messages permission.")
                except discord.HTTPException:
                    pass
                return

    # Process commands normally
    await bot.process_commands(message)

# Safety check if TOKEN is missing
if not TOKEN:
    raise ValueError("TOKEN environment variable is not set (Railway → Variables).")

bot.run(TOKEN)
