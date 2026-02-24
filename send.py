import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")  # Railway environment variable

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")

@bot.event
async def on_message(message: discord.Message):
    # Ignore bots
    if message.author.bot:
        return

    # Ignore DMs
    if not message.guild:
        return

    guild = message.guild
    owner = guild.owner

    # OWNER BYPASS (important)
    if message.author == owner:
        await bot.process_commands(message)
        return

    # Block @everyone / @here
    if message.mention_everyone:
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, you are not allowed to use @everyone or @here.",
                delete_after=5
            )
        except discord.Forbidden:
            pass
        return

    # Block pinging the owner
    if owner and owner in message.mentions:
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, you cannot ping the server owner.",
                delete_after=5
            )
        except discord.Forbidden:
            pass
        return

    await bot.process_commands(message)

bot.run(TOKEN)