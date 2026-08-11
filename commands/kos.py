"""
Used to check a users KoS status (KoS, previously KoS, not KoS).
"""
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import logging
import config

logger = logging.getLogger(__name__)
API_URL = config.API_URL


class Kos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='kos', description="Check users KoS status")
    @app_commands.describe(username="Roblox username")
    async def kos(self, interaction: discord.Interaction, username: str | None = None):
        """
        Used to check the defined users KoS status.
        Args:
            interaction: The interaction object from discord.Interaction.
            username: The username of the user to be checked, defaults to the interaction.user's server nick.
        """
        await interaction.response.defer()
        if not username:
            username = interaction.user.nick
        api_key = config.API_KEY

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_URL}/koscheck/{username}", headers=headers) as resp:
                    data = await resp.json()
                    if resp.status == 200:
                        status = data.get("status")
                        if status == "current_kos":
                            msg = f"**{data["username"]}** is **KoS**."
                            embed = discord.Embed(
                                description=msg,
                                color=discord.Color.green()
                            )
                        elif status == "former_kos":
                            msg = f"**{data["username"]}** is **not KoS**.\n-# {data["username"]} was previously KoS."
                            embed = discord.Embed(
                                description=msg,
                                color=discord.Color.red()
                            )
                        else:
                            msg = f"**{data["username"]}** is **not KoS**."
                            embed = discord.Embed(
                                description=msg,
                                color=discord.Color.red()
                            )
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send(
                            f"An error occurred while checking the users KoS status: {data.get("error", "Status check failed")}")
        except Exception as e:
            logger.error(f"An error occurred while checking the users ({username}) KoS status: {e}")
            await interaction.followup.send(
                "An error occurred while checking the users KoS status. Please try again later. If this error persist, please contact <@926037474805948416>.")


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(Kos(bot))
