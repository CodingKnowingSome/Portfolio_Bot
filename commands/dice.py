"""
dice.py: Lets the user roll a random number in a given range.
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
        Gets a random number between 1 and the maximum, outputs it as an ephemeral response.
        :param interaction: discord.Interaction
        :param amount: Maximum value on the dice.
        """
        num = random.randint(1, int(amount + 1))
        await interaction.response.send_message(f"{interaction.user.mention} you rolled: {num}", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Setup.
    :param bot: The bot.
    """
    await bot.add_cog(Dice(bot))
