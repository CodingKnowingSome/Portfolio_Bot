"""
Command used by Overwatch+ to reset the Officer leaderboard.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import aiosqlite
from datetime import datetime
from Functions.access_check import required_role
import config

logger = logging.getLogger(__name__)


class LeaderboardReset(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='leaderboardreset', description="Resets the leaderboard.")
    @required_role(config.OVERWATCH_ROLE_ID)
    async def leaderboardreset(self, interaction: discord.Interaction):
        """
        Copies the leaderboard into the archive channel, sets every "graded" to 0 in the database.
        Args:
            interaction: The interaction object from discord.Interaction.

        Returns: NA

        """
        await interaction.response.defer(ephemeral=True)
        async with aiosqlite.connect("data/leaderboard.db") as conn:
            async with conn.execute("SELECT * FROM leaderboard") as c:
                all_officer = await c.fetchall()
        processed_officer = []
        guild = self.bot.get_guild(config.TEST_GUILD_ID)
        if not guild:
            try:
                guild = await self.bot.fetch_guild(config.TEST_GUILD_ID)
            except Exception as e:
                logger.error(f"Could not fetch guild: {e}.")
                return
        description = ""
        for user_id, graded, total in all_officer:
            user = guild.get_member(user_id)
            if not user:
                try:
                    user = await guild.fetch_member(user_id)
                except Exception as e:
                    user = None
                    logger.warning(f"Failed to fetch member {user_id}: {e}")
            has_in_role = False
            if user:
                has_in_role = user.get_role(config.IN_ROLE_ID) is not None
                user_display = user.nick
                user_name = user_display.split("|")[0].strip()
            else:
                user_name = f"*Deleted/Unknown User ({user_id})*"
            is_inactive = 1 if has_in_role else 0
            processed_officer.append((
                is_inactive,
                graded or 0,
                total or 0,
                user_name,
                has_in_role
            ))
        processed_officer.sort(key=lambda x: (x[0], -x[1]))
        for idx, (is_inactive, graded, total, user_name, has_in_role) in enumerate(processed_officer, start=1):
            if not has_in_role:
                description += f"**{idx}.** - {user_name} - {graded} ({total})\n"
            else:
                description += f"**{idx}.** - {user_name} - ⛔ ({total})\n"
        embed = discord.Embed(title="Leaderboard", color=discord.Color.yellow())
        if not description:
            description = "NA"
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
        async with aiosqlite.connect("data/leaderboard.db") as conn:
            await conn.execute("UPDATE leaderboard SET graded = 0")
            await conn.commit()
        self.bot.dispatch("leaderboard_update", "officer")
        await interaction.followup.send("Leaderboard archived and reset.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(LeaderboardReset(bot))