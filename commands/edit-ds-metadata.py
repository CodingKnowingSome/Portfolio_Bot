import discord
import logging
import sqlite3
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


class EditDSMetadata(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="edit-ds-metadata", description="Edit your duty state metadata")
    @app_commands.describe(username="Your new username.")
    @app_commands.describe(timezone="Your new timezone (GMT±X).")
    async def edit_ds_metadata(self, interaction: discord.Interaction, username: str = None, timezone: str = None):
        """
        Command used to edit your duty state metadata.
        Args:
            interaction: The interaction object from discord.Interaction.
            username: The new username to include in the metadata as str.
            timezone: The new timezone to include in the metadata as str.
        """
        if username:
            with sqlite3.connect("data/ds_metadata.db") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM ds_metadata WHERE user_id = ?", (interaction.user.id,))
                metadata = c.fetchone()
                conn.commit()
            if metadata:
                with sqlite3.connect("data/ds_metadata.db") as conn:
                    c = conn.cursor()
                    c.execute("UPDATE ds_metadata SET username = ? WHERE user_id = ?", (username, interaction.user.id))
                    conn.commit()
        if timezone:
            with sqlite3.connect("data/ds_metadata.db") as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM ds_metadata WHERE user_id = ?", (interaction.user.id,))
                metadata = c.fetchone()
                conn.commit()
            if metadata:
                with sqlite3.connect("data/ds_metadata.db") as conn:
                    c = conn.cursor()
                    c.execute("UPDATE ds_metadata SET timezone = ? WHERE user_id = ?", (timezone, interaction.user.id))
                    conn.commit()
        if not username and not timezone:
            await interaction.response.send_message("Nothing to edit.", ephemeral=True)
        else:
            if timezone and not username:
                text = "Timezone"
            elif username and not timezone:
                text = "Username"
            else:
                text = "Timezone and username"
            text += " updated."
            await interaction.response.send_message(text, ephemeral=True)


async def setup(bot: commands.Bot):
    """
    Command setup.
    Args:
        bot: The bot.
    """
    await bot.add_cog(EditDSMetadata(bot))
