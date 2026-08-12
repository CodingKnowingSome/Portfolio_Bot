"""
Called when a duty state is denied, handles the grading channel message deletion and notifies the user.
"""
import discord
from datetime import datetime
import config
import logging
import sqlite3

logger = logging.getLogger(__name__)


async def deny(client: discord.Client, message: discord.Message, user: discord.User, reason: str, interaction: discord.Interaction):
    """
    Deletes the images and info message in the grading channel, notifies the user with an embed.
    Args:
        reason: The reason for the denial as a str.
        client: The bot.
        message: The duty state message as discord.Message.
        user: The user grading the duty state as discord.User.
        interaction: The interaction object from discord.Interaction.

    Returns: NA

    """
    await interaction.response.defer()
    with sqlite3.connect("data/duty_states.db") as conn:
        c = conn.cursor()
        c.execute("SELECT message_id FROM fetches WHERE message_id = ?", (message.id,))
        row = c.fetchone()
    if not row:
        await interaction.followup.send("This duty state was already graded.", ephemeral=True)
        return
    with sqlite3.connect("data/duty_states.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM fetches WHERE message_id = ?", (message.id,))
        conn.commit()
    embed = discord.Embed(
        title="Denied",
        description=f"{message.author.mention} your duty state has been denied by {user.mention}",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )

    embed.add_field(name="Reason: ", value=reason)
    await message.reply(embed=embed)
    await message.clear_reactions()
    await message.add_reaction("❌")
    await interaction.followup.send(f"Duty state denied. Reason: {reason}", ephemeral=True)