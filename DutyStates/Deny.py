"""
Called when a duty state is denied, handles the grading channel message deletion and notifies the user.
"""
import discord
from datetime import datetime
import config
import logging
import sqlite3

logger = logging.getLogger(__name__)


async def deny(client: discord.Client, message: discord.Message, img1: discord.Message, img2: discord.Message,
               img3: discord.Message, user: discord.User, fetch_msg: discord.Message, reason: str):
    """
    Deletes the images and info message in the grading channel, notifies the user with an embed.
    Args:
        reason: The reason for the denial as a str.
        client: The bot.
        message: The duty state message as discord.Message.
        img1: The duty proof image in the grading channel as discord.Message.
        img2: The tablist started image in the grading channel as discord.Message.
        img3: The tablist ended image in the grading channel as discord.Message.
        user: The user grading the duty state as discord.User.
        fetch_msg: The message with the duty state info as discord.Message.

    Returns: NA

    """
    dsgrade_channel_id = config.DSGRADE_CHANNEL_ID
    gchannel = client.get_channel(dsgrade_channel_id)
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
    try:
        with sqlite3.connect("data/duty_states.db") as conn:
            c = conn.cursor()
            c.execute("DELETE FROM fetches WHERE message_id = ?", (message.id,))
            conn.commit()
    except Exception as e:
        await gchannel.send("Could not delete the embed images!")
        print(f"Could not delete the embed images! {img1.id} | {img2.id} | {img3.id}", e)
