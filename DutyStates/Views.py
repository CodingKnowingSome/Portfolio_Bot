"""
Permanent fetch button class.
"""
import discord
from DutyStates.Fetch import fetch


class PersistentFetchView(discord.ui.View):
    def __init__(self, bot: discord.Client):
        super().__init__(timeout=None)
        self.bot = bot

    # noinspection PyUnusedLocal
    @discord.ui.button(
        label="fetch a duty state!",
        style=discord.ButtonStyle.primary,
        custom_id="ds:persistent_fetch_button"
    )
    async def fetch_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        """
        Calls the fetch function for duty state fetching in the grading channel.
        Args:
            interaction: The interaction object from discord.Interaction.
            button: I don't know, it takes 3 arguments.
        """
        await fetch(self.bot, interaction.user)
