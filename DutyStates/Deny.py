"""
The function that handles the duty state denials.
"""
import discord
from datetime import datetime
import config
import logging

logger = logging.getLogger(__name__)


async def deny(client: discord.Client, message: discord.Message, img1: discord.Message, img2: discord.Message,
               img3: discord.Message, user: discord.User, fetch_msg: discord.Message, reason: str):
    """
    Handles the duty state denial notification, and grade channel messages deletion.
    :param client: The bot.
    :param message: The duty state message.
    :param img1: The duty proof image in the grading channel.
    :param img2: The tablist started image in the grading channel.
    :param img3: The tablist ended image in the grading channel.
    :param user: The user who graded the duty state.
    :param fetch_msg: The message containing the duty state information in the grading channel.
    :param reason:
    """
    dsgrade_channel_id = config.DSGRADE_CHANNEL_ID
    gchannel = client.get_channel(dsgrade_channel_id)
    embed = discord.Embed(
        title="Denied",
        description=f"{message.author.mention} your duty state has been denied by {user.mention}",
        color=discord.Color.red()
    )

    embed.add_field(name="Reason: ", value=reason)
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed.set_footer(text=f"{currenttime}")
    await message.reply(embed=embed)
    await message.clear_reactions()
    await message.add_reaction("❌")
    embed = fetch_msg.embeds[0]
    embed.color = discord.Color.red()
    embed.set_footer(text=f"Denied! | {reason}")
    await fetch_msg.edit(embed=embed, view=None)
    await fetch_msg.delete()
    try:
        await img1.delete()
        await img2.delete()
        await img3.delete()
    except Exception as e:
        await gchannel.send("Could not delete the embed images!")
        print(f"Could not delete the embed images! {img1.id} | {img2.id} | {img3.id}", e)
