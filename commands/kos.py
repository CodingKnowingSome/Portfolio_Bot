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
                    if resp.status == 200 and data.get("success"):
                        status = data.get("status")
                        if status == "current_kos":
                            msg = f"**{data.get("username")}** is **KoS**."
                            embed = discord.Embed(
                                description=msg,
                                color=discord.Color.green()
                            )
                        elif status == "former_kos":
                            msg = f"**{data.get("username")}** is **not KoS**.\n-# {data.get("username")} was previously KoS."
                            embed = discord.Embed(
                                description=msg,
                                color=discord.Color.gold()
                            )
                        else:
                            msg = f"**{data.get("username")}** is **not KoS**."
                            embed = discord.Embed(
                                description=msg,
                                color=discord.Color.red()
                            )
                        await interaction.followup.send(embed=embed)
                    else:
                        error_msg = data.get("detail") or data.get("error") or "Status check failed."
                        logger.error(f"FastAPI error in /kos for {username}: {error_msg}")
                        await interaction.followup.send(
                            f"An error occurred while checking KoS status for {username}: {error_msg}", ephemeral=True
                        )
        except aiohttp.ClientError as e:
            logger.error(f"Network error in /kos for {username}: {e}")
            await interaction.followup.send(f"Failed to reach the API server\n*Error log:*\n```{e}```",
                                            ephemeral=True)
        except Exception as e:
            logger.error(f"Unexpected error in /kos for {username}: {e}")
            await interaction.followup.send(f"An unexpected error occurred\n*Error log:*\n```{e}```",
                                            ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(Kos(bot))
