"""
Generates and outputs a random number in the range defined by user from 1.
"""
import discord
from discord import app_commands
from discord.ext import commands
import random
import logging

logger = logging.getLogger(__name__)


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dice", description="Roll a dice")
    @app_commands.describe(amount="The biggest number on the dice (integer)")
    async def dice(self, interaction: discord.Interaction, amount: int):
        """
        Generates a random number from the range defined by user from 1, and outputs it as an ephemeral.
        Args:
            interaction: The interaction object from discord.Interaction.
            amount: The maximum amount the user can roll input by the user.
        """
        num = random.randint(1, int(amount + 1))
        await interaction.response.send_message(f"{interaction.user.mention} you rolled: {num}", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(Dice(bot))
