import discord
from discord.ext import commands
from discord import app_commands
import logging
import sqlite3
from datetime import datetime
from access_check import has_required_role

logger = logging.getLogger(__name__)

class LeaderboardReset(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='leaderboardreset', description="Resets the leaderboard.")
    async def leaderboardreset(self, interaction: discord.Interaction):
        OVERWATCH_ROLE_ID = 1526677577367032008
        if not await has_required_role(interaction, OVERWATCH_ROLE_ID):
            return
        conn = sqlite3.connect("data/leaderboard.db")
        c = conn.cursor()
        c.execute("SELECT * FROM leaderboard")
        all = c.fetchall()
        all.sort(key=lambda x: x[1], reverse=True)
        description = ""
        for idx, (user_id, graded) in enumerate(all, start=1):
            try:
                user = await self.bot.fetch_user(user_id)
                description += f"**{idx}.** - {user.mention} - {graded}\n"
            except Exception:
                description += f"**{idx}.** - *Deleted/Unknown User ({user_id})* - {graded}\n"
        embed = discord.Embed(title="Leaderboard", color=discord.Color.yellow())
        embed.description = f"Quota was reset by: {interaction.user.mention} at {datetime.now()}. Leaderboard at that moment:\n" + description
        embed.set_footer(text=f"Updated: {datetime.now()}")
        archive_channel_id = 1526692371486736464
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
        await interaction.response.send_message("Leaderboard archived and reset.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(LeaderboardReset(bot))