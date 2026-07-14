import logging
logger = logging.getLogger(__name__)
async def GeneralChecker(message):
    if "furios"in message.content.lower():
        await message.channel.send("https://tenor.com/view/cat-angry-furious-furios-gif-26039002")
    else:
        return
