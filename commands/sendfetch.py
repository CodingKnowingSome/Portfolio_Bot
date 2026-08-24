"""
Sends a new duty state fetch message.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import config

from Functions.Views import PersistentFetchView
from Functions.access_check import has_required_role

logger = logging.getLogger(__name__)


class SendFetch(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="sendfetch", description="Send the duty state fetch message again.")
    async def sendfetch(self, interaction: discord.Interaction):
        """
        Sends a new duty state fetch message (Admin).
        Args:
            interaction: The interaction object from discord.Interaction.

        Returns: NA

        """
        admin_role_id = config.ADMIN_ROLE_ID
        if not await has_required_role(interaction, admin_role_id):
            return
        channel = self.bot.get_channel(config.DSGRADE_CHANNEL_ID)
        if not channel:
            channel = await self.bot.fetch_channel(config.DSGRADE_CHANNEL_ID)
        officer_id = config.OFFICER_ROLE_ID
        officer_role = discord.utils.get(interaction.guild.roles, id=officer_id)
        if not officer_role:
            try:
                officer_role = await interaction.guild.fetch_role(officer_id)
            except discord.NotFound:
                logger.warning("Could not find officer role.")
                await interaction.response.send_message("Could not find officer role.", ephemeral=True)
                return
        payload = {
            "flags": 32768,
            "allowed_mentions": {"roles": [str(officer_role.id)]},
            "components": [
                {
                    "type": 17,
                    "accent_color": 0x3498DB,
                    "components": [
                        {
                            "type": 10,
                            "content": (
                                f"{officer_role.mention}\n\n"
                                f"# Fetch a duty state!\n"
                                f"Press the below button to fetch a duty state! "
                                f"You can fetch again and get the same if needed."
                            )
                        },
                        {
                            "type": 1,
                            "components": [
                                {
                                    "type": 2,
                                    "style": 1,
                                    "label": "Fetch a duty state!",
                                    "custom_id": "ds:persistent_fetch"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        route = discord.http.Route('POST', '/channels/{channel_id}/messages', channel_id=channel.id)
        await self.bot.http.request(route, json=payload)
        await interaction.response.send_message("fetch added.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(SendFetch(bot))
    bot.add_view(PersistentFetchView(bot, "Fetch a Duty State", "ds:persistent_fetch"))
