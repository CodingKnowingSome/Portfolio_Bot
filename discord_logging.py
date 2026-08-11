"""
Handles logging in the discord channel.
"""
import logging
import discord
import asyncio

logger = logging.getLogger(__name__)


class DiscordLogHandler(logging.Handler):
    """
    The discord logging handler.
    """

    def __init__(self, bot: discord.Client, channel_id: int, ping_role_id: int):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id
        self.ping_role_id = ping_role_id
        self._is_sending = False

    def emit(self, record):
        """
        Emits not logged logs and creates the embed.
        Args:
            record: The record to emit or include in the embed.

        Returns: NA

        """
        if not self.bot.is_ready() or self.bot.is_closed():
            return
        if self._is_sending:
            return
        log_entry = self.format(record)
        if len(log_entry) > 1800:
            log_entry = log_entry[:1750] + "\n... [Cut due to Discord character limit.]"
        if record.levelno == logging.ERROR:
            color = discord.Color.red()
            title = "Error log"
        elif record.levelno == logging.CRITICAL:
            color = discord.Color.dark_red()
            title = "Critical log"
        elif record.levelno == logging.WARNING:
            color = discord.Color.orange()
            title = "Warning log"
        else:
            return
        embed = discord.Embed(
            title=title,
            color=color,
            description=f"```python\n{log_entry}\n```"
        )
        embed.add_field(name='Logger', value=record.name)
        embed.add_field(name='Level', value=record.levelname)
        asyncio.run_coroutine_threadsafe(self.send_log(embed), self.bot.loop)

    async def send_log(self, embed: discord.Embed):
        """
        Sends the log in the designated Discord channel.
        Args:
            embed: The embed containing the log.
        """
        self._is_sending = True
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                channel = await self.bot.fetch_channel(self.channel_id)

            if channel:
                await channel.send(content=f'<@&{self.ping_role_id}>', embed=embed)
        except Exception as e:
            logger.error(e)
        finally:
            self._is_sending = False
