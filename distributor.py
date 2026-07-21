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
    Distributes the messages to different handlers based on the channel they were sent in.
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
        Distributes the messages to different handlers based on the channel they were sent in.
        :param message: The message.
        :return:
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
        Calls the duty_listener function for the message in duty states.
        :param message:
        """
        await Events.DutyListener.dutylistener(message)

    @staticmethod
    async def general(message: discord.Message):
        """
        Calls the general function with the message.
        :param message: The message.
        """
        await Events.General.generalchecker(message)
