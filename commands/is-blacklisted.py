"""
Checks if a user is blacklisted or not.
"""
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import logging
import config

logger = logging.getLogger(__name__)
API_URL = config.API_URL


class IsBlacklisted(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="is-blacklisted", description="Check if a user is blacklisted")
    @app_commands.describe(username="Roblox username")
    async def is_blacklisted(self, interaction: discord.Interaction, username: str | None = None):
        """
        Checks if a user is blacklisted or not.
        Args:
            interaction: The interaction object from discord.Interaction.
            username: The user to be checked (optional, defaults to the interaction.user.nick)
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
                async with session.get(f"{API_URL}/blacklist/{username}", headers=headers) as resp:
                    data = await resp.json()
                    if resp.status == 200:
                        status = data.get("status")
                        if status is True and data.get("blacklist"):
                            embed = discord.Embed(
                                title="Blacklist",
                                color=discord.Color.red(),
                            )
                            entry = data.get("blacklist")[0]
                            embed.add_field(name="Username", value=entry.get("username", username))
                            embed.add_field(name="Reason", value=entry.get("reason", "No reason provided."),
                                            inline=False)
                            embed.add_field(name="Last edited", value=f"<t:{entry.get('last_edit')}:R>",
                                            inline=False)
                            await interaction.followup.send(embed=embed)
                        else:
                            embed = discord.Embed(
                                title="Blacklist",
                                color=discord.Color.green(),
                                description=f"{username} is not blacklisted."
                            )
                            await interaction.followup.send(embed=embed)
                    else:
                        error_msg = data.get("detail") or data.get("error") or "Status check failed (unknown)."
                        logger.error(f"FastAPI error in /is-blacklisted for {username}: {error_msg}")
                        await interaction.followup.send(
                            f"An error occurred while checking blacklsit status: {error_msg}", ephemeral=True
                        )
        except aiohttp.ClientError as e:
            logger.error(f"Network error in /is-blacklisted for {username}: {e}")
            await interaction.followup.send(f"Failed to reach the API server\n*Error log:*\n```{e}```",
                                            ephemeral=True)
        except Exception as e:
            logger.error(f"Unexpected error in /is-blacklisted for {username}: {e}")
            await interaction.followup.send(f"An unexpected error occurred\n*Error log:*\n```{e}```",
                                            ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(IsBlacklisted(bot))
