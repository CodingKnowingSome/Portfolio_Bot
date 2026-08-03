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
        await interaction.response.defer()
        if not username:
            username = interaction.user.nick
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{API_URL}/koscheck/{username}") as resp:
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
                        await interaction.followup.send(f"An error occurred while checking the users KoS status: {data.get("error", "Status check failed")}")
        except Exception as e:
            logger.error(f"An error occurred while checking the users ({username}) KoS status: {e}")
            await interaction.followup.send("An error occurred while checking the users KoS status. Please try again later. If this error persist, please contact <@926037474805948416>.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Kos(bot))