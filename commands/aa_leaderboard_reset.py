"""
Command used by Officer+ to reset the AA leaderboard.
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


class AALeaderboardReset(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='aaleaderboardreset', description="Resets the AA leaderboard.")
    @required_role(config.OFFICER_ROLE_ID)
    async def aaleaderboardreset(self, interaction: discord.Interaction):
        """
        Copies the AA leaderboard into an archive channel, changes every weekly lesson to 0 in the AA database.
        Args:
            interaction: The interaction object from discord.Interaction.

        Returns: NA

        """
        await interaction.response.defer(ephemeral=True)
        async with aiosqlite.connect("data/leaderboard.db") as conn:
            async with conn.execute("SELECT * FROM aa_leaderboard") as c:
                all_staff = await c.fetchall()
        processed_staff = []
        guild = self.bot.get_guild(config.TEST_GUILD_ID)
        if not guild:
            try:
                guild = await self.bot.fetch_guild(config.TEST_GUILD_ID)
            except Exception as e:
                logger.error(f"Could not fetch guild: {e}.")
                return
        description = ""
        for user_id, lessons, total in all_staff:
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
            processed_staff.append((
                is_inactive,
                lessons or 0,
                total or 0,
                user_name,
                has_in_role
            ))
        processed_staff.sort(key=lambda x: (x[0], -x[1]))
        for idx, (is_inactive, lessons, total, user_name, has_in_role) in enumerate(processed_staff, start=1):
            if not has_in_role:
                description += f"**{idx}.** - {user_name} - {lessons} ({total})\n"
            else:
                description += f"**{idx}.** - {user_name} - ⛔ ({total})\n"
        embed = discord.Embed(title="Leaderboard", color=discord.Color.yellow())
        if not description:
            description = "NA"
        embed.description = f"Quota was reset by: {interaction.user.mention} at {datetime.now()}. leaderboard at that moment:\n" + description
        embed.set_footer(text=f"Updated: {datetime.now()}")
        archive_channel_id = config.AA_LD_ARCHIVE_ID
        archive_channel = self.bot.get_channel(archive_channel_id)
        if not archive_channel:
            try:
                archive_channel = await self.bot.fetch_channel(archive_channel_id)
            except discord.NotFound:
                await interaction.response.send_message("Archive channel not found.", ephemeral=True)
                return
        await archive_channel.send(embed=embed)
        async with aiosqlite.connect("data/leaderboard.db") as conn:
            await conn.execute("UPDATE aa_leaderboard SET lessons = 0")
            await conn.commit()
        self.bot.dispatch("leaderboard_update", "aa")
        await interaction.followup.send("Leaderboard archived and reset.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(AALeaderboardReset(bot))