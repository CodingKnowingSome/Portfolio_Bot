"""
Command to send a new data request embed and select menu.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import config
from Functions.access_check import required_role
from Functions.Data_Handling.DataRequestsView import DataRequestsView

logger = logging.getLogger(__name__)


class DataMessage(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="send-data-req", description="Send the data request message again. (Admin+)")
    @required_role(config.ADMIN_ROLE_ID)
    async def datamessage(self, interaction: discord.Interaction):
        """
        Sends a new data request embed and select menu. Admin restricted.
        Args:
            interaction: The interaction object from discord.Interaction.

        Returns: NA

        """
        channel = self.bot.get_channel(config.DATA_CHANNEL_ID)
        if not channel:
            await self.bot.fetch_channel(config.DATA_CHANNEL_ID)
        embed = discord.Embed(
            title="Request about your data",
            color=discord.Color.blue(),
            description="Request all of your stored data (with limitations), request deletion of your stored data (with limitations). You *must* have your DMs open."
        )
        embed.add_field(name="Request Data", value="Request your stored data.", inline=False)
        embed.add_field(name="Request Data Removal", value="Request the removal of your stored data.", inline=False)
        embed.set_footer(text="Use the below selection to begin the process.")
        embed.set_thumbnail(
            url="https://www.citypng.com/public/uploads/preview/hd-python-logo-symbol-transparent-png-735811696257415dbkifcuokn.png")

        await channel.send(embed=embed, view=DataRequestsView())
        await interaction.response.send_message("Message successfully sent.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(DataMessage(bot))
