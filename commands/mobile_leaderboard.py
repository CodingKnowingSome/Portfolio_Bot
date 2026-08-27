import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands
from Functions.access_check import has_required_role
import config
import datetime
import logging
from Functions.cache_members import get_member

logger = logging.getLogger(__name__)


class MobileLeaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mobileleaderboard", description="Leaderboard for mobile users.")
    @app_commands.choices(leaderboard=[
        app_commands.Choice(name="AA", value="aa"),
        app_commands.Choice(name="Officer", value="officer")
    ])
    async def mobileleaderboard(self, interaction: discord.Interaction, leaderboard: str):
        if leaderboard == "aa":
            can = await has_required_role(interaction, config.AA_ROLE_ID)
            if not can:
                return
            await interaction.response.defer(ephemeral=True)
            embed = discord.Embed(title="Leaderboard", color=discord.Color.yellow())
            async with aiosqlite.connect("data/leaderboard.db") as conn:
                async with conn.execute("SELECT * FROM aa_leaderboard") as c:
                    all_staff = await c.fetchall()
            processed_staff = []
            for user_id, graded, total in all_staff:
                user = await get_member(interaction.guild, user_id)
                has_in_role = False
                if user:
                    has_in_role = user.get_role(config.IN_ROLE_ID) is not None
                    user_display = user.nick
                    user_name = user_display.split("|")[0].strip()
                else:
                    user_name = f"*Deleted/Unknown User*"
                is_inactive = 1 if has_in_role else 0
                processed_staff.append((is_inactive, graded or 0, total or 0, user_name, has_in_role))
            processed_staff.sort(key=lambda x: (x[0], -x[1]))
            description = "The weekly and all time lesson counts of Staff members.\n\n"
            for idx, (is_inactive, graded, total, user_name, has_in_role) in enumerate(processed_staff, start=1):
                if not has_in_role:
                    description += f"**{idx}.** - {user_name} - {graded} ({total})\n"
                else:
                    description += f"**{idx}.** - {user_name} - ⛔ ({total})\n"
            ctime = int(datetime.datetime.now().timestamp())
            description += f"\n-# Last updated: <t:{ctime}:T>"
            embed.description = description if description else "NA"
            await interaction.followup.send(embed=embed, ephemeral=True)
        if leaderboard == "officer":
            can = await has_required_role(interaction, config.OFFICER_ROLE_ID)
            if not can:
                return
            await interaction.response.defer(ephemeral=True)
            embed = discord.Embed(title="Leaderboard", color=discord.Color.yellow())
            async with aiosqlite.connect("data/leaderboard.db") as conn:
                async with conn.execute("SELECT * FROM leaderboard") as c:
                    all_officer = await c.fetchall()
            processed_officers = []
            for user_id, graded, total in all_officer:
                user = await get_member(interaction.guild, user_id)
                has_in_role = False
                if user:
                    has_in_role = user.get_role(config.IN_ROLE_ID) is not None
                    user_display = user.nick
                    user_name = user_display.split("|")[0].strip()
                else:
                    user_name = f"*Deleted/Unknown User*"
                is_inactive = 1 if has_in_role else 0
                processed_officers.append((is_inactive, graded or 0, total or 0, user_name, has_in_role))
            processed_officers.sort(key=lambda x: (x[0], -x[1]))
            description = "The weekly and all time duty states graded counts of Officers.\n\n"
            for idx, (is_inactive, graded, total, user_name, has_in_role) in enumerate(processed_officers, start=1):
                if not has_in_role:
                    description += f"**{idx}.** - {user_name} - {graded} ({total})\n"
                else:
                    description += f"**{idx}.** - {user_name} - ⛔ ({total})\n"
            ctime = int(datetime.datetime.now().timestamp())
            description += f"\n-# Last updated: <t:{ctime}:T>"
            embed.description = description if description else "NA"
            await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(MobileLeaderboard(bot))
