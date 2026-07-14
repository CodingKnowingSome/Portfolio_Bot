import logging
import discord
import asyncio

class DiscordLogHandler(logging.Handler):
    def __init__(self, bot, channel_id, ping_role_id):
        super().__init__()
        self.bot = bot
        self.channel_id = channel_id
        self.ping_role_id = ping_role_id

    def emit(self, record):
        if record.name.startswith("discord"):
            return
        if not self.bot.is_ready() or self.bot.is_closed():
            return
        log_entry = self.format(record)
        if len(log_entry) > 1800:
            log_entry = log_entry[:1750] +"/n... [Cut due to Discord character limit.]"
        if record.levelno == logging.ERROR:
            color = discord.Color.red()
            title = "Error log"
        else:
            color = discord.Color.orange()
            title = "Warning log"
        embed = discord.Embed(
            title = title,
            color = color,
            description=f"```python\n{log_entry}\n```"
        )
        embed.add_field(name='Logger', value=record.name, inline=True)
        embed.add_field(name='Level', value=record.levelname, inline=True)
        asyncio.run_coroutine_threadsafe(self.send_log(embed), self.bot.loop)
    async def send_log(self, embed):
        try:
            channel = self.bot.get_channel(self.channel_id)
            if not channel:
                channel = await self.bot.fetch_channel(self.channel_id)

            if channel:
                await channel.send(content=f'<@&{self.ping_role_id}>', embed=embed)
        except Exception as e:
            print(e)