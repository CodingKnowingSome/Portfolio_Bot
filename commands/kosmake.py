"""
Used to edit a users KoS status.
"""
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import logging
import config
from Functions.access_check import has_required_role

logger = logging.getLogger(__name__)
API_URL = config.API_URL


class KosMake(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='kosmake', description="Add or remove a user from the KoS database.")
    @app_commands.describe(username="Roblox username")
    @app_commands.describe(status="KoS status of user (True/False)")
    @app_commands.choices(status=[
        app_commands.Choice(name="True", value="True"),
        app_commands.Choice(name="False", value="False"),
    ])
    async def kosmake(self, interaction: discord.Interaction, username: str, status: str):
        """
        Edits a user's KoS status.
        Args:
            interaction: The interaction object from discord.Interaction.
            username: The username of the user to be edited.
            status: The KoS status of the user as a boolean.

        Returns: NA

        """
        tester_role_id = config.TESTER_ROLE_ID
        if not await has_required_role(interaction, tester_role_id):
            return
        await interaction.response.defer()
        if status == "True":
            status = True
        elif status == "False":
            status = False
        else:
            pass
        payload = {"username": username, "status": status}
        api_key = config.API_KEY

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{API_URL}/kos", json=payload, headers=headers) as resp:
                    data = await resp.json()
                    if resp.status == 200 and data["success"]:
                        state_str = "ADDED to" if status is True else "REMOVED from"
                        await interaction.followup.send(
                            f"**{data["username"]}** ({data["user_id"]}) {state_str} KoS database.", ephemeral=True)
                    else:
                        await interaction.followup.send(f"Error: {data("error", "Failed to update KoS status.")}")
        except Exception as e:
            logger.error(f"Error in /kosmake: {e}")


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(KosMake(bot))
