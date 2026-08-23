"""
Deny modal for the duty state grader to input the denial reason.
"""
from discord.ui import Modal, TextInput
import discord
from DutyStates.Deny import deny
import logging

logger = logging.getLogger(__name__)


class DenyModal(Modal):
    def __init__(self, client: discord.Client, message: discord.Message, user: discord.User):
        super().__init__(title="Reason for denial: ")
        # noinspection PyTypeChecker
        self.reason = TextInput(label="Reason for denial: ", style=discord.TextStyle.paragraph)
        self.add_item(self.reason)
        self.client = client
        self.message = message
        self.user = user

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason.value
        #await interaction.response.send_message(f"Reason: {reason}", ephemeral=True)
        await deny(self.message, self.user, reason, interaction)
