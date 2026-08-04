"""
Called when a duty state is accepted, handles the grading channel message deletion and notifies the user.
"""
import discord
from datetime import datetime
import config
import logging

logger = logging.getLogger(__name__)


async def accept(client: discord.Client, message: discord.Message, img1: discord.Message, img2: discord.Message,
                 img3: discord.Message, user: discord.User, fetch_msg: discord.Message, total_mins: int):
    """
    Calls points_check to check for the given points, creates and sends the embed, deletes the info message and
    images in the grading channel.
    Args:
        client: The bot.
        message: The duty state message as discord.Message.
        img1: The duty proof image in the grading channel as discord.Message.
        img2: The tablist started image in the grading channel as discord.Message.
        img3: The tablist ended image in the grading channel as discord.Message.
        user: The user grading the duty state as discord.User.
        fetch_msg: The message with the duty state info as discord.Message.
        total_mins: The total time of the duty states as int.

    Returns: NA

    """
    dsgrade_channel_id = config.DSGRADE_CHANNEL_ID
    gchannel = client.get_channel(dsgrade_channel_id)

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
        color=discord.Color.green()
    )

    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed.set_footer(text=f"{currenttime}")
    await message.reply(embed=embed)
    await message.clear_reactions()
    await message.add_reaction("✔️")
    await fetch_msg.delete()
    try:
        await img1.delete()
        await img2.delete()
        await img3.delete()
    except Exception as e:
        await gchannel.send("Could not delete the embed images!")
        print(f"Could not delete the embed images! {img1.id} | {img2.id} | {img3.id}", e)
