import os
import discord
from discord.ext import commands

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("No TOKEN found in environment variables!")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user} (ID: {bot.user.id})")

@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    if message.guild is None:
        return

    guild = message.guild
    owner = guild.owner

    # Owner bypass
    if owner and message.author.id == owner.id:
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
            print("Missing permissions: Manage Messages")
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
            print("Missing permissions: Manage Messages")
        return

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.run(TOKEN)
