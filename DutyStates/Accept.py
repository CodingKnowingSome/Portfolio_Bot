"""
Called when a duty state is accepted, handles the grading channel message deletion and notifies the user.
"""
import discord
from datetime import datetime
import logging
import sqlite3

logger = logging.getLogger(__name__)


async def accept(client: discord.Client, message: discord.Message, user: discord.User, total_mins: int,
                 interaction: discord.Interaction):
    """
    Calls points_check to check for the given points, creates and sends the embed, deletes the info message and
    images in the grading channel.
    Args:
        client: The bot.
        message: The duty state message as discord.Message.
        user: The user grading the duty state as discord.User.
        total_mins: The total time of the duty states as int.
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

    def points_check(time: int) -> int:
        """
        Checks for the amount of points given by the duty state length.
        Args:
            time: The length of the duty state as int.

        Returns: The amount of points given as int.

        """
        if time < 2 * 60:
            return 1
        elif time < 4 * 60:
            return 2
        elif time < 6 * 60:
            return 3
        elif time < 8 * 60:
            return 4
        elif time < 10 * 60:
            return 5
        elif time < 15 * 60:
            return 6
        elif time < 20 * 60:
            return 7
        elif time < 24 * 60:
            return 8
        else:
            return 9

    points = points_check(total_mins)

    embed = discord.Embed(
        title="Accepted",
        description=f"{message.author.mention} your duty state has been accepted by {user.mention}. You have earned {points} point(s).",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    await message.reply(embed=embed)
    await message.clear_reactions()
    await message.add_reaction("✔️")
    await interaction.followup.send("Duty state accepted.", ephemeral=True)
