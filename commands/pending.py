from discord.ext import commands
from discord import app_commands
import discord
import sqlite3
import logging
from access_check import has_required_role

logger = logging.getLogger(__name__)

class Pending(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pending", description="Check for your pending duty states!")
    async def pending(self, interaction: discord.Interaction):
        GUEST_ROLE_ID = 1526372106517086370
        if not await has_required_role(interaction, GUEST_ROLE_ID):
            return
        conn = sqlite3.connect("data/duty_states.db")
        c = conn.cursor()
        c.execute("SELECT * FROM pending_duties WHERE user_id = ?", (interaction.user.id,))
        results = c.fetchall()
        if len(results) > 0:
            await interaction.response.send_message(f"{interaction.user.mention}, you have {len(results)} duty state(s) pending.", ephemeral=True)
        else:
            await interaction.response.send_message(f"You have no duty states pending, {interaction.user.mention}!", ephemeral=True)
async def setup(bot: commands.Bot):
    await bot.add_cog(Pending(bot))