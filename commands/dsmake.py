"""
Creates the Duty State text for user based on metadata and inputs.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import sqlite3
from discord.ui import Modal, TextInput
from access_check import has_required_role
import config

logger = logging.getLogger(__name__)


class DSMake(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='dsmake', description="Create a duty state.")
    @app_commands.describe(start_time="Start time of the duty state.")
    @app_commands.describe(end_time="End time of the duty state.")
    @app_commands.describe(duty="Duty")
    @app_commands.describe(duty_link="Link to duty screenshot.")
    @app_commands.describe(start_tablist="Link to Tablist Started")
    @app_commands.describe(end_tablist="Link to Tablist Ended")
    async def dsmake(self, interaction: discord.Interaction, start_time: str, end_time: str, duty: str, duty_link: str,
                     start_tablist: str, end_tablist: str):
        """
        Creates a Duty State text for user based on metadata and inputs, and outputs it as an ephemeral response.
        :param interaction: discord.Interaction
        :param start_time: Starting time of the duty state
        :param end_time: Ending time of the duty state
        :param duty: Duty.
        :param duty_link: Link of the duty screenshot.
        :param start_tablist: Link to Tablist Started.
        :param end_tablist: Link to Tablist Ended.
        :return:
        """
        guest_role_id = config.GUEST_ROLE_ID
        if not await has_required_role(interaction, guest_role_id):
            return
        conn = sqlite3.connect("data/ds_metadata.db")
        c = conn.cursor()
        c.execute('''SELECT * FROM ds_metadata WHERE user_id = ?''', (interaction.user.id,))
        results = c.fetchone()
        if not results:
            modal = GetMetadata()
            await interaction.response.send_modal(modal)
        else:
            await interaction.response.send_message(
                f"Username: {results[1]}\nDuty: {duty}\n{duty_link}\n\nTime Started: {start_time} {results[2]}\nTablist Started: {start_tablist}\n\nTime Ended: {end_time} {results[2]}\nTablist Ended: {end_tablist}",
                ephemeral=True)


class GetMetadata(Modal):
    def __init__(self):
        super().__init__(title="Metadata to create your duty states")
        self.data = TextInput(label='Format: {username} | {timezone}', style=discord.TextStyle.paragraph)
        self.add_item(self.data)

    async def on_submit(self, interaction: discord.Interaction):
        data = self.data.value
        data_split = data.split('|')
        if len(data_split) != 2:
            await interaction.response.send_message("You did not follow the format. Try again.", ephemeral=True)
        else:
            user_id = interaction.user.id
            username = data_split[0]
            timezone = data_split[1]
            conn = sqlite3.connect("data/ds_metadata.db")
            c = conn.cursor()
            c.execute("""INSERT INTO ds_metadata VALUES (?,?,?)""", (user_id, username, timezone))
            conn.commit()
            conn.close()
            await interaction.response.send_message(
                f"{username}'s data has been added - you can create duty states now.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Setup.
    :param bot: The bot.
    """
    await bot.add_cog(DSMake(bot))