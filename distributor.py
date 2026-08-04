"""
Distributes messages to different handlers based on the channel they were sent in.
"""
import discord
import Events
import logging
import config

logger = logging.getLogger(__name__)


class Distribute:
    """
    Class with the functions responsible for distributing messages to different handlers.
    """

    def __init__(self):
        self.handlers = {
            "duty_listener": {
                "channels": {config.DS_CHANNEL_ID},
                "function": self.duty_listener
            }
        }

    async def handle(self, message: discord.Message):
        """
        Decides which handler to use.
        Args:
            message: The message as discord.Message.

        Returns: Calls the correct handler based on the channel passing in the message.

        """
        if message.author.bot:
            return None
        for handler in self.handlers.values():
            if message.channel.id in handler["channels"]:
                return await handler["function"](message)
        else:
            return await self.general(message)

    @staticmethod
    async def duty_listener(message: discord.Message):
        """
        Calls the duty state handler.
        Args:
            message: The message as discord.Message.
        """
        await Events.DutyListener.dutylistener(message)

    @staticmethod
    async def general(message: discord.Message):
        """
        Calls the general message handler.
        Args:
            message: The message as discord.Message.
        """
        await Events.General.generalchecker(message)
