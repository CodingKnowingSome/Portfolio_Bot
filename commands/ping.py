"""
Checks and responds with the latency of the bot.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging

logger = logging.getLogger(__name__)


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='ping', description="Replies with the bot's latency.")
    async def ping(self, interaction: discord.Interaction):
        """
        Responds with the bot's latency.
        Args:
            interaction: The interaction object from discord.Interaction.
        """
        latency = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"The bot's latency is {latency}ms")


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(Ping(bot))
