"""
Add/Remove someone to/from the blacklist database.
"""
from datetime import datetime
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
import logging
import config
from access_check import has_required_role

logger = logging.getLogger(__name__)
API_URL = config.API_URL


class Blacklist(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='blacklist', description="Add or remove a user from the blacklist database.")
    @app_commands.describe(username="Roblox username")
    @app_commands.describe(reason="Reason for adding a user to the blacklist database.")
    @app_commands.describe(action="Add or remove a blacklist (Add/Remove).")
    @app_commands.choices(action=[
        app_commands.Choice(name="Add", value="add"),
        app_commands.Choice(name="Remove", value="remove"),
    ])
    async def blacklist(self, interaction: discord.Interaction, username: str, action: app_commands.Choice[str],
                        reason: str = "No reason provided."):
        """
        Adds/Removes a user from the blacklist database, with reason by calling the blacklist API endpoint.
        Args:
            interaction: The interaction object from discord.Interaction.
            username: The username of the user.
            action: Add or remove the user.
            reason: The reason for the said action.

        Returns: NA

        """
        tester_role_id = config.TESTER_ROLE_ID
        if not await has_required_role(interaction, tester_role_id):
            return
        await interaction.response.defer()
        if action.value == "add":
            action_str = "add"
        else:
            action_str = "remove"
        payload = {
            "username": username,
            "action": action_str,
            "reason": reason,
            "added_by": interaction.user.id
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{API_URL}/blacklist", json=payload) as resp:
                    data = await resp.json()
                    if resp.status == 200 and data.get("success"):
                        if action.value == "remove":
                            embed = discord.Embed(
                                title="Blacklist removed",
                                color=discord.Color.green()
                            )
                            embed.add_field(name="Username", value=f"**{data["username"]}** ({data["user_id"]})")
                            embed.add_field(name="Reason", value=f"{reason}")
                            embed.add_field(name="Added by", value=f"{interaction.user.mention}")
                            embed.set_footer(text=f"Time: {datetime.now()}")
                            await interaction.followup.send(embed=embed, ephemeral=False)
                        else:
                            embed = discord.Embed(
                                title="Blacklist added",
                                color=discord.Color.red()
                            )
                            embed.add_field(name="Username", value=f"**{data["username"]}** ({data["user_id"]})")
                            embed.add_field(name="Reason", value=f"{reason}")
                            embed.add_field(name="Added by", value=f"{interaction.user.mention}")
                            embed.set_footer(text=f"Time: {datetime.now()}")
                            await interaction.followup.send(embed=embed, ephemeral=False)
                    else:
                        await interaction.followup.send(
                            f"An error occurred while while adding/removing user. Please try again later. If this error persists, please contact <@926037474805948416>.",
                            ephemeral=True)

        except Exception as e:
            logger.error(f"Error in /blacklist: {e}")
            await interaction.followup.send(
                f"An error occurred while while adding/removing user. Please try again later. If this error persists, please contact <@926037474805948416>.",
                ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(Blacklist(bot))
