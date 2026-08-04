"""
Sends a new duty state fetch message.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import config

from DutyStates.Views import PersistentFetchView
from access_check import has_required_role

logger = logging.getLogger(__name__)


class SendFetch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sendfetch", description="Send the duty state fetch message again.")
    async def sendfetch(self, interaction: discord.Interaction):
        """
        Sends a new duty state fetch message (Admin).
        Args:
            interaction: The interaction object from discord.Interaction.

        Returns: NA

        """
        admin_role_id = config.ADMIN_ROLE_ID
        if not await has_required_role(interaction, admin_role_id):
            return

        channel = self.bot.get_channel(config.DSGRADE_CHANNEL_ID)
        embed = discord.Embed(
            title="fetch a duty state!",
            color=discord.Color.blue()
        )
        view = PersistentFetchView(self.bot)
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message("fetch added.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(SendFetch(bot))
    bot.add_view(PersistentFetchView(bot))
