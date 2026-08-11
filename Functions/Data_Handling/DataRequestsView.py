"""
Permanent selection menu for the data requests.
"""
import discord
from Functions.Data_Handling.Request import request
from Functions.Data_Handling.Removal import removal
import logging

logger = logging.getLogger(__name__)


class DataRequestsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Request Data",
                description="Receive a copy of all stored personal data (limitations apply).",
                value="request_data"
            ),
            discord.SelectOption(
                label="Request Data Removal",
                description="Request permanent deletion of your stored data (limitations apply).",
                value="request_removal"
            ),
        ]
        super().__init__(placeholder="Choose an option...", options=options, custom_id="data_requests:select")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.message.edit(view=self.view)
        selected_value = self.values[0]

        if selected_value == "request_data":
            await request(interaction.client, interaction.user, interaction.user.nick)
            await interaction.followup.send(
                "Your data request has been logged. The bot will contact you shortly. Please have your DMs open.",
                ephemeral=True
            )
        elif selected_value == "request_removal":
            await removal(interaction.client, interaction.user, interaction.user.nick)
            await interaction.followup.send(
                "Your data removal request has been submitted to staff for processing. Please have your DMs open.",
                ephemeral=True
            )


class DataRequestsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(DataRequestsSelect())
