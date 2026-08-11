"""
Calculates Kylo's weight, and it is % to becoming a blackhole.
"""
import discord
import random
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)


# noinspection PyDunderSlots,PyUnresolvedReferences
class Kylo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="kylo", description="Calculates Kylo's weight")
    async def kylo(self, interaction: discord.Interaction):
        """
        Calculates Kylo's weight, and it is % to becoming a blackhole.
        Args:
            interaction:
        """
        embed = discord.Embed(
            title="Kylo's Weight"
        )
        embed_colors = {
            "blackhole": discord.Color.red(),
            "high": discord.Color.orange(),
            "medium": discord.Color.yellow(),
            "low": discord.Color.green()
        }
        weight_minimum = 1000
        weight_max = int(8.75 * (10 ** 25))
        weight = random.randint(weight_minimum, weight_max)
        percent = round((weight / weight_max) * 100)
        embed.description = f"Kylo's weight is {weight:,} kg, {percent}% to becoming a blackhole."
        embed.set_footer(text="For legal reasons, this is merely a joke, and the Kylo name is just there as a name.")
        if percent == 100:
            embed.color = embed_colors["blackhole"]
        elif 100 > percent > 100 * 2 / 3:
            embed.color = embed_colors["high"]
        elif 100 * 2 / 3 > percent > 100 / 3:
            embed.color = embed_colors["medium"]
        else:
            embed.color = embed_colors["low"]
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(Kylo(bot))
