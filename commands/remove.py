import discord
import aiosqlite
from discord.ext import commands
from discord import app_commands
from Functions.access_check import has_required_role
import config
from datetime import datetime


class Remove(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="remove", description="Remove a user from one of the leaderboards.")
    @app_commands.describe(user="The user to remove.")
    @app_commands.choices(leaderboard=[
        app_commands.Choice(name="AA", value="aa"),
        app_commands.Choice(name="Officer", value="officer"),
    ])
    async def remove(self, interaction: discord.Interaction, user: discord.Member,
                     leaderboard: str):
        table = {
            "aa": ["aa_leaderboard", config.OFFICER_ROLE_ID, config.AA_LD_ARCHIVE_ID],
            "officer": ["leaderboard", config.OVERWATCH_ROLE_ID, config.ARCHIVE_CHANNEL_ID]
        }
        can = await has_required_role(interaction, table[leaderboard][1])
        if not can:
            return
        await interaction.response.defer(ephemeral=True)
        table_name = table[leaderboard][0]
        async with aiosqlite.connect("data/leaderboard.db") as conn:
            async with conn.execute(f"SELECT * FROM {table_name} WHERE user_id = ?", (user.id,)) as c:
                row = await c.fetchone()
            async with conn.execute(f"DELETE FROM {table_name} WHERE user_id = ?", (user.id,)) as c:
                count = c.rowcount
            await conn.commit()
        if count:
            embed = discord.Embed(
                title=f"{user.name} removed from {table_name}",
                description=f"Removed by: {interaction.user.mention}\nAll time data: {row[2]}",
                timestamp=datetime.now()
            )
            arch_channel = interaction.guild.get_channel(table[leaderboard][2])
            if not arch_channel:
                try:
                    arch_channel = await interaction.guild.fetch_channel(table[leaderboard][2])
                    await arch_channel.send(f"{user.mention}", embed=embed)
                except discord.NotFound:
                    pass
            try:
                await arch_channel.send(f"{user.mention}", embed=embed)
            except discord.Forbidden:
                pass
            await interaction.followup.send(f"{user.mention} has been removed from {table_name}.")
            self.bot.dispatch("leaderboard_update", f"{leaderboard}")
        else:
            await interaction.followup.send(f"{user.mention} is not in {table_name}.")


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(Remove(bot))
