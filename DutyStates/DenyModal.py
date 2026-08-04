"""
Deny modal for the duty state grader to input the denial reason.
"""
from discord.ui import Modal, TextInput
import discord
from DutyStates.Deny import deny
import logging

logger = logging.getLogger(__name__)


class DenyModal(Modal):
    def __init__(self, client: discord.Client, message: discord.Message, img1: discord.Message, img2: discord.Message,
                 img3: discord.Message, user: discord.User, fetch_msg: discord.Message):
        super().__init__(title="Reason for denial: ")
        self.reason = TextInput(label="Reason for denial: ", style=discord.TextStyle.paragraph)
        self.add_item(self.reason)
        self.client = client
        self.message = message
        self.img1 = img1
        self.img2 = img2
        self.img3 = img3
        self.user = user
        self.fetch_msg = fetch_msg

    async def on_submit(self, interaction: discord.Interaction):
        reason = self.reason.value
        await interaction.response.send_message(f"Reason: {reason}", ephemeral=True)
        await deny(self.client, self.message, self.img1, self.img2, self.img3, self.user, self.fetch_msg, reason)
