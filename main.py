"""
The main file, responsible for starting the bot, and calling other functions.
"""
import discord
from discord.ext import commands
import os
import logging
import database_setup
import asyncio
import config
from DutyStates.Leaderboard import leaderboard
from AA.AA_Leaderboard import aaleaderboard
from distributor import Distribute
from logs import setup_logging
from discord_logging import DiscordLogHandler
from AA.AA_Promotions_Shouts import aa_promotions_shouts
from AA.AA_Leaderboard_Edit import aa_leaderboard_edit
from Functions.IN_Handler import in_handler, in_deny_handler
from access_check import has_required_role_member
from Functions.IN_Remove_Handler import in_remove_handler
from api import run_api
import threading

#logging setup
setup_logging()
logger = logging.getLogger(__name__)

#intents setup
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True
intents.reactions = True
intents.members = True

TEST_GUILD_ID = config.TEST_GUILD_ID


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None, intents=intents)

    async def setup_hook(self):
        log_channel_id = config.LOG_CHANNEL_ID
        ping_role_id = config.PING_ROLE_ID
        discord_handler = DiscordLogHandler(client, log_channel_id, ping_role_id)
        discord_handler.setLevel(logging.WARNING)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        discord_handler.setFormatter(formatter)
        logging.getLogger().addHandler(discord_handler)
        logger.info('Discord logging setup complete.')
        logger.info('Loading databases')
        await database_setup.database_setup()
        logger.info('Databases loaded')
        logger.info('Loading leaderboard...')
        asyncio.create_task(leaderboard(self))
        logger.info('leaderboard loaded')
        logger.info('Loading AA leaderboard...')
        asyncio.create_task(aaleaderboard(self))
        logger.info('AA leaderboard loaded')
        logger.info('Loading commands...')
        for filename in os.listdir('./commands'):
            if filename.endswith('.py') and filename != '__init__.py':
                cog_name = filename[:-3]
                try:
                    await self.load_extension(f"commands.{cog_name}")
                    logger.info(f'Loaded {cog_name}')
                except Exception as e:
                    logger.error(f'Failed to load {cog_name}, {e}', exc_info=True)
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
    """
    Prints and logs when the bot is logged in and ready.
    """
    print('We have logged in as {0.user}'.format(client))
    logger.info('We have logged in as {0.user}'.format(client))
    logger.info('Bot is up and running.')
    logger.warning('Discord logging TEST warning. Ignore.')

if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    print("APIs started.")

#$hello for testing
@client.event
async def on_message(message: discord.Message):
    """
    Hands messages to the distributor.
    :param message: The message.
    :return:
    """
    if message.author.bot:
        return
    elif message.content.startswith('$hello'):
        await message.channel.send('Hello!')
    else:
        await distributor.handle(message)


@client.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """
    Handles the event when a reaction is added to send AA promotion shout if needed.
    :param payload: The data of the reaction.
    :return:
    """
    aa_logs_channel_id = config.AA_LOGS_CHANNEL_ID
    in_channel_id = config.IN_CHANNEL_ID
    if payload.channel_id == aa_logs_channel_id:
        if payload.emoji.name == "aa_approve":
            channel = client.get_channel(payload.channel_id)
            guild = client.get_guild(payload.guild_id)
            try:
                message = await channel.fetch_message(payload.message_id)
            except discord.NotFound:
                return
            await aa_promotions_shouts(message, client, guild)
            await aa_leaderboard_edit(message, guild)
        else:
            return
    elif payload.channel_id == in_channel_id:
        if payload.emoji.name == "aa_approve":
            reactor = payload.user_id
            guild = client.get_guild(payload.guild_id)
            valid1 = await has_required_role_member(guild, reactor, config.OFFICER_ROLE_ID)
            valid2 = await has_required_role_member(guild, reactor, config.OVERWATCH_ROLE_ID)
            if valid1 or valid2:
                channel = client.get_channel(payload.channel_id)
                guild = client.get_guild(payload.guild_id)
                try:
                    message = await channel.fetch_message(payload.message_id)
                except discord.NotFound:
                    return
                await in_handler(message, guild)
            else:
                return
        elif payload.emoji.name == "aa_deny":
            reactor = payload.user_id
            guild = client.get_guild(payload.guild_id)
            valid1 = await has_required_role_member(guild, reactor, config.OFFICER_ROLE_ID)
            valid2 = await has_required_role_member(guild, reactor, config.OVERWATCH_ROLE_ID)
            if valid1 or valid2:
                channel = client.get_channel(payload.channel_id)
                guild = client.get_guild(payload.guild_id)
                try:
                    message = await channel.fetch_message(payload.message_id)
                except discord.NotFound:
                    return
                await in_deny_handler(message, guild)
            else:
                return
    else:
        return

@client.event
async def on_message_delete(message: discord.Message):
    if message.channel.id == config.IN_CHANNEL_ID:
        guild = client.get_guild(config.TEST_GUILD_ID)
        if not guild:
            await client.fetch_guild(config.TEST_GUILD_ID)
        await in_remove_handler(message, guild)

client.run(config.DISCORD_TOKEN)
