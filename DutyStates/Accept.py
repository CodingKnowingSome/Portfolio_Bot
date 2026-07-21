"""
The function that handles the duty state acceptances.
"""
import discord
from datetime import datetime
import config
import logging

logger = logging.getLogger(__name__)


async def accept(client: discord.Client, message: discord.Message, img1: discord.Message, img2: discord.Message,
                 img3: discord.Message, user: discord.User, fetch_msg: discord.Message, total_mins: int):
    """
    Handles the duty state acceptance. Calculates points, deletes the grading channel messages, sends the notification.
    :param client: The bot.
    :param message: The duty state message.
    :param img1: The duty proof image in the grading channel.
    :param img2: The tablist started image in the grading channel.
    :param img3: The tablist ended image in the grading channel.
    :param user: The user who graded the duty state.
    :param fetch_msg: The message containing the duty state information in the grading channel.
    :param total_mins: The length of the duty state in minutes.
    :return:
    """
    dsgrade_channel_id = config.DSGRADE_CHANNEL_ID
    gchannel = client.get_channel(dsgrade_channel_id)

    def points_check(time: int) -> int:
        """
        Checks the given amount of points for the given duty state length.
        :param time: Length of the duty state, calculated in fetch.py.
        :return:
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
