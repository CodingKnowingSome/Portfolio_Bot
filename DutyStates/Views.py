import discord
from DutyStates.Fetch import Fetch

class PersistentFetchView(discord.ui.View):
    def __init__(self, bot: discord.Client):
        super().__init__(timeout=None)
        self.bot = bot

    # Rule 2: Create a decorator button and assign a completely unique custom_id
    @discord.ui.button(
        label="Fetch a duty state!",
        style=discord.ButtonStyle.primary,
        custom_id="ds:persistent_fetch_button"
    )
    async def fetch_button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await Fetch(self.bot, interaction.user, interaction.message)