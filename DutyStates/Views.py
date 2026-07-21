"""
Permanent fetch button class.
"""
import discord
from DutyStates.Fetch import fetch


class PersistentFetchView(discord.ui.View):
    def __init__(self, bot: discord.Client):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="fetch a duty state!",
        style=discord.ButtonStyle.primary,
        custom_id="ds:persistent_fetch_button"
    )
    async def fetch_button_callback(self, interaction: discord.Interaction):
        """
        Calls the fetch function.
        :param interaction: discord.Interaction
        """
        await fetch(self.bot, interaction.user)
