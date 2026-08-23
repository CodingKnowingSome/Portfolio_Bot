"""
Creates a formatted duty state based on the user inputs and collected metadata.
"""
import discord
from discord.ext import commands
from discord import app_commands
import logging
import aiosqlite
from discord.ui import Modal, TextInput
from Functions.access_check import has_required_role
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
        Creates the duty state based on the user inputs and collected metadata, if there is no metadata for the user
        calls a modal to ask for it.
        Args:
            interaction: The interaction object from discord.Interaction.
            start_time: The starting time of the duty state.
            end_time: The ending time of the duty state.
            duty: The name of the duty.
            duty_link: The link to the duty proof.
            start_tablist: The link to the start tablist screenshot.
            end_tablist: The link to the end tablist screenshot.

        Returns: NA

        """
        guest_role_id = config.GUEST_ROLE_ID
        if not await has_required_role(interaction, guest_role_id):
            return
        async with aiosqlite.connect("data/ds_metadata.db") as conn:
            async with conn.execute('''SELECT * FROM ds_metadata WHERE user_id = ?''', (interaction.user.id,)) as c:
                results = await c.fetchone()
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
        # noinspection PyTypeChecker
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
            async with aiosqlite.connect("data/ds_metadata.db") as conn:
                await conn.execute("""INSERT INTO ds_metadata VALUES (?,?,?)""", (user_id, username, timezone))
                await conn.commit()
            await interaction.response.send_message(
                f"{username}'s data has been added - you can create duty states now.", ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(DSMake(bot))