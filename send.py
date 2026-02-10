from discord import ui
import discord

# ================= CONFIG =================
GUILD_ID = 1449298346425585768  # server to unban from

ALLOWED_USERS = {
    1258115928525373570,  # nico044037
    123456789012345678   # sukunaluni ← replace with real ID
}

def allowed(user: discord.User | discord.Member):
    return user.id in ALLOWED_USERS

# ================= UNBAN BUTTON =================
class UnbanRequestView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🔓 Unban", style=discord.ButtonStyle.primary)
    async def unban_button(
        self,
        interaction: discord.Interaction,
        button: ui.Button
    ):
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
