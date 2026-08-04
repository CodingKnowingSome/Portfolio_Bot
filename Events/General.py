"""
Checks for misc responses.
"""
#TODO: Add more stuff here.
import logging
import discord

logger = logging.getLogger(__name__)


async def generalchecker(message: discord.Message):
    """
    Cheks if a message contains 'furios', responds with the gif if so.
    Args:
        message: The message as discord.Message.

    Returns: NA

    """
    if "furios" in message.content.lower():
        await message.channel.send("https://tenor.com/view/cat-angry-furious-furios-gif-26039002")
    else:
        return
