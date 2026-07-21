"""
Checks for misc responses.
"""
import logging
import discord

logger = logging.getLogger(__name__)


async def generalchecker(message: discord.Message):
    """
    Check if the message contains "furios" and responds if it does.
    :param message: The message.
    :return:
    """
    if "furios" in message.content.lower():
        await message.channel.send("https://tenor.com/view/cat-angry-furious-furios-gif-26039002")
    else:
        return
