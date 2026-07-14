import Events
import logging
logger = logging.getLogger(__name__)
class Distribute:
    def __init__(self):
        self.handlers = {
            "duty_listener":{
                "channels": {1526379960179232818},
                "function": self.duty_listener
            }
        }
    async def handle(self, message):
        if message.author.bot:
            return
        for handler in self.handlers.values():
            if message.channel.id in handler["channels"]:
                return await handler["function"](message)
            else:
                return await self.general(message)

    async def duty_listener(self, message):
        await Events.DutyListener.DutyListener(message)
    async def general(self, message):
        await Events.General.GeneralChecker(message)
