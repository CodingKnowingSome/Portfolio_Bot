"""
Reset the leaderboard.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import sqlite3
from datetime import datetime
from access_check import has_required_role
import config

logger = logging.getLogger(__name__)


class LeaderboardReset(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='leaderboardreset', description="Resets the leaderboard.")
    async def leaderboardreset(self, interaction: discord.Interaction):
        """
        Resets the leaderboard.
        :param interaction: discord.Interaction.
        :return:
        """
        overwatch_role_id = config.OVERWATCH_ROLE_ID
        if not await has_required_role(interaction, overwatch_role_id):
            return
        conn = sqlite3.connect("data/leaderboard.db")
        c = conn.cursor()
        c.execute("SELECT * FROM leaderboard")
        all_officer = c.fetchall()
        all_officer.sort(key=lambda x: x[1], reverse=True)
        description = ""
        for idx, (user_id, graded) in enumerate(all_officer, start=1):
            try:
                user = await self.bot.fetch_user(user_id)
                description += f"**{idx}.** - {user.mention} - {graded}\n"
            except Exception:
                description += f"**{idx}.** - *Deleted/Unknown User ({user_id})* - {graded}\n"
        embed = discord.Embed(title="leaderboard", color=discord.Color.yellow())
        embed.description = f"Quota was reset by: {interaction.user.mention} at {datetime.now()}. leaderboard at that moment:\n" + description
        embed.set_footer(text=f"Updated: {datetime.now()}")
        archive_channel_id = config.ARCHIVE_CHANNEL_ID
        archive_channel = self.bot.get_channel(archive_channel_id)
        if not archive_channel:
            try:
                archive_channel = await self.bot.fetch_channel(archive_channel_id)
            except discord.NotFound:
                await interaction.response.send_message("Archive channel not found.", ephemeral=True)
                return
        await archive_channel.send(embed=embed)
        conn = sqlite3.connect("data/leaderboard.db")
        c = conn.cursor()
        c.execute("UPDATE leaderboard SET graded = 0")
        conn.commit()
        conn.close()
        await interaction.response.send_message("leaderboard archived and reset.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Setup.
    :param bot: The bot.
    """
    await bot.add_cog(LeaderboardReset(bot))