import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import database_setup
import asyncio
from DutyStates.Leaderboard import Leaderboard
from distributor import Distribute
from logs import setup_logging

#dotenv setup
load_dotenv()
TOKEN=os.getenv('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError('DISCORD_TOKEN environment variable is not set')

#intents setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.reactions = True
intents.members = True


#logging setup
setup_logging()
logger = logging.getLogger(__name__)

TEST_GUILD_ID = 1526366475642998935

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None, intents=intents)
    async def setup_hook(self):
        logger.info('Loading databases')
        await database_setup.database_setup()
        logger.info('Databases loaded')
        logger.info('Loading Leaderboard...')
        asyncio.create_task(Leaderboard(self))
        logger.info('Leaderboard loaded')
        logger.info('Loading commands...')
        for filename in os.listdir('./commands'):
            if filename.endswith('.py') and filename != '__init__.py':
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f"commands.{cog_name}")
                    logger.info(f'Loaded {cog_name}')
                except Exception as e:
                    logger.error(f'Failed to load {cog_name}', exc_info=True)
        try:
            logger.info('Copying into test guild.')
            guild_object = discord.Object(id=TEST_GUILD_ID)
            self.tree.copy_global_to(guild=guild_object)
            synced = await self.tree.sync(guild=guild_object)
            logger.info(f'Synced {len(synced)} command(s).')
        except Exception as e:
            logger.error(f'Failed to sync command to the test guild: {e}', exc_info=True)
        for filename in os.listdir("./Events"):
            if filename.endswith(".py"):
                module = __import__(f"Events.{filename[:-3]}", fromlist=["setup"])
                if hasattr(module, "setup"):
                    module.setup(client)

client = Bot()
distributor = Distribute()
#on_ready logging
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    logger.info('We have logged in as {0.user}'.format(client))
    logger.info('Bot is up and running.')

#$hello for testing
@client.event
async def on_message(message):
    if message.author.bot:
        return
    elif message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    else:
        await distributor.handle(message)



client.run(TOKEN)
