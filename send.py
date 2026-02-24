import os
import discord
from discord.ext import commands
from discord import app_commands

# ================== CONFIG ==================
TOKEN = os.getenv("TOKEN")

# PUT YOUR ANNOUNCEMENT CHANNEL ID HERE
ANNOUNCEMENT_CHANNEL_ID = 1471946689085706459  # CHANGE THIS

# BLOCKED ROLE PING IDS
BLOCKED_ROLE_IDS = {
    1449303642359468166,
    1449317587488866416,
    1470459777665466604,
    1451273696823083129,
    1454978722582106288
}
# ===========================================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    allowed_mentions=discord.AllowedMentions.none()
)

tree = bot.tree

# ================== APPROVE / DECLINE VIEW ==================
class ApproveDeclineView(discord.ui.View):
    def __init__(self, requester: discord.User, message: str, guild: discord.Guild):
        super().__init__(timeout=None)
        self.requester = requester
        self.message = message
        self.guild = guild

    @discord.ui.button(label="Approve", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.requester.id:
            await interaction.response.send_message(
                "Only the requester can approve this announcement.",
                ephemeral=True
            )
            return

        channel = self.guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)

        if not channel:
            await interaction.response.send_message(
                "Announcement channel not found. Check the channel ID.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📢 Announcement",
            description=self.message,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Approved by {interaction.user}")

        await channel.send(embed=embed)
        await interaction.response.edit_message(
            content="✅ Announcement approved and sent!",
            view=None
        )

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.requester.id:
            await interaction.response.send_message(
                "Only the requester can decline this announcement.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="❌ Announcement Declined",
            description="Your announcement request has been declined.",
            color=discord.Color.red()
        )

        try:
            await self.requester.send(embed=embed)
        except:
            pass

        await interaction.response.edit_message(
            content="❌ Announcement declined.",
            view=None
        )

# ================== SLASH COMMAND: /announce ==================
@tree.command(name="announce", description="Request an announcement")
@app_commands.describe(message="The announcement message")
async def announce(interaction: discord.Interaction, message: str):
    user = interaction.user
    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True
        )
        return

    view = ApproveDeclineView(user, message, guild)

    embed = discord.Embed(
        title="📨 Announcement Request",
        description=message,
        color=discord.Color.orange()
    )
    embed.set_footer(text="Approve to send to the announcement channel.")

    try:
        await user.send(embed=embed, view=view)
        await interaction.response.send_message(
            "📬 Check your DMs to approve or decline the announcement.",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I can't DM you. Enable DMs from server members.",
            ephemeral=True
        )

# ================== SLASH COMMAND: /info ==================
@tree.command(name="info", description="Show server information")
async def info(interaction: discord.Interaction):
    guild = interaction.guild

    if guild is None:
        await interaction.response.send_message(
            "This command can only be used in a server.",
            ephemeral=True
        )
        return

    try:
        owner = guild.owner or await guild.fetch_member(guild.owner_id)
        owner_text = f"{owner} ({owner.id})"
    except:
        owner_text = f"Unknown ({guild.owner_id})"

    embed = discord.Embed(
        title=f"📊 Server Info - {guild.name}",
        color=discord.Color.blurple()
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(name="🆔 Server ID", value=str(guild.id), inline=False)
    embed.add_field(name="👑 Owner", value=owner_text, inline=False)
    embed.add_field(name="👥 Members", value=str(guild.member_count), inline=True)
    embed.add_field(
        name="📅 Created On",
        value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=True
    )
    embed.add_field(
        name="💎 Boost Level",
        value=f"Level {guild.premium_tier} ({guild.premium_subscription_count or 0} boosts)",
        inline=True
    )
    embed.add_field(name="💬 Text Channels", value=str(len(guild.text_channels)), inline=True)
    embed.add_field(name="🔊 Voice Channels", value=str(len(guild.voice_channels)), inline=True)
    embed.add_field(name="🗂️ Categories", value=str(len(guild.categories)), inline=True)
    embed.add_field(name="🎭 Roles", value=str(len(guild.roles)), inline=True)
    embed.add_field(name="😀 Emojis", value=str(len(guild.emojis)), inline=True)

    embed.set_footer(text=f"Requested by {interaction.user}")

    await interaction.response.send_message(embed=embed)

# ================== READY EVENT ==================
@bot.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {bot.user}")
    print("Anti-ping + /announce + /info system ACTIVE.")

# ================== ANTI-PING SYSTEM ==================
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or not message.guild:
        return

    guild = message.guild

    try:
        owner = guild.owner or await guild.fetch_member(guild.owner_id)
    except:
        owner = None

    # OWNER BYPASS
    if owner and message.author.id == owner.id:
        await bot.process_commands(message)
        return

    should_delete = False

    # Block @everyone / @here
    if (
        message.mention_everyone
        or "@everyone" in message.content
        or "@here" in message.content
    ):
        should_delete = True

    # Block owner pings
    if owner:
        if (
            owner in message.mentions
            or f"<@{owner.id}>" in message.content
            or f"<@!{owner.id}>" in message.content
        ):
            should_delete = True

    # Block protected role pings
    for role in message.role_mentions:
        if role.id in BLOCKED_ROLE_IDS:
            should_delete = True
            break

    for role_id in BLOCKED_ROLE_IDS:
        if f"<@&{role_id}>" in message.content:
            should_delete = True
            break

    if should_delete:
        try:
            await message.delete()
            await message.channel.send(
                f"{message.author.mention}, that ping is not allowed.",
                delete_after=4
            )
        except discord.Forbidden:
            print("Missing Manage Messages permission.")
        except discord.HTTPException:
            pass
        return

    await bot.process_commands(message)

# ================== START BOT ==================
if not TOKEN:
    raise ValueError("TOKEN is not set! Add it in Railway → Variables.")

bot.run(TOKEN)
