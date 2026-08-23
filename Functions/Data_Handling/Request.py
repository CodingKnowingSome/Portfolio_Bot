"""
Handles data requests.
"""
import discord
import config
from Functions.get_roblox_id import get_roblox_id
import aiosqlite
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


async def request(bot: discord.Client, user: discord.User, username: str):
    """
    Handles the data requests. Sends the user all of their stored personal data. Only exception is the user that blacklisted them.
    Args:
        bot: The bot as discord.Client.
        user: The user using the command as discord.User.
        username: The username of the user using the command as str.
    """
    log_channel_id = config.DATA_LOG_CHANNEL_ID
    discord_id = user.id
    roblox_id, exact_username = await get_roblox_id(username)

    if roblox_id:
        async with aiosqlite.connect("data/kos_blacklist.db") as conn:
            async with conn.execute("SELECT * FROM kos WHERE user_id = ?", (roblox_id,)) as c:
                kos_row = await c.fetchone()
            async with conn.execute("SELECT * FROM blacklist WHERE user_id = ?", (roblox_id,)) as c:
                blacklist = await c.fetchone()
    async with aiosqlite.connect("data/duty_states.db") as conn:
        async with conn.execute("SELECT * FROM pending_duties WHERE user_id = ?", (discord_id,)) as c:
            pending_duties = await c.fetchall()
    async with aiosqlite.connect("data/leaderboard.db") as conn:
        async with conn.execute("SELECT * FROM leaderboard WHERE user_id = ?", (discord_id,)) as c:
            leaderboard = await c.fetchone()
        async with conn.execute("SELECT * FROM aa_leaderboard WHERE user_id = ?", (discord_id,)) as c:
            aa_leaderboard = await c.fetchone()
    async with aiosqlite.connect("data/ds_metadata.db") as conn:
        async with conn.execute("SELECT * FROM ds_metadata WHERE user_id = ?", (discord_id,)) as c:
            ds_metadata = await c.fetchone()
    user_embed = discord.Embed(
        title="Portfolio Bot Stored Data",
        color=discord.Color.blue(),
        timestamp=datetime.now(),
        description="Here is all of your personal data stored by our bot."
    )
    user_embed.add_field(
        name="Discord Information (For the command to lookup your stored data, temporary)",
        value=f"{user.name} ({user.id}), your server nick.",
        inline=False
    )
    if roblox_id:
        user_embed.add_field(
            name="Roblox Information (For the command to lookup KoS and blacklist storage, temporary)",
            value=f"{exact_username} ({roblox_id})",
            inline=False
        )
    if kos_row:
        user_embed.add_field(
            name="KoS Information",
            value=f"ID: {kos_row[0]}, status: {kos_row[1]}",
            inline=False
        )
    if blacklist:
        user_embed.add_field(
            name="Blacklist Information",
            value=f"ID: {blacklist[0]}, reason: {blacklist[1]}, last edited: {blacklist[3]}",
            inline=False
        )
    if pending_duties:
        duties = ""
        for row in pending_duties:
            duties += f"{row[0]}\n"
        user_embed.add_field(
            name="Pending Duty States",
            value=f"ID: {user.id}, messages:\n{duties}",
            inline=False
        )
    if leaderboard:
        user_embed.add_field(
            name="Leaderboard Information",
            value=f"ID: {leaderboard[0]}, graded: {leaderboard[1]}, total: {leaderboard[2]}",
            inline=False
        )
    if aa_leaderboard:
        user_embed.add_field(
            name="AA Leaderboard Information",
            value=f"ID: {aa_leaderboard[0]}, lessons: {aa_leaderboard[1]}, total: {aa_leaderboard[2]}",
            inline=False
        )
    if ds_metadata:
        user_embed.add_field(
            name="Duty State Metadata",
            value=f"ID: {ds_metadata[0]}, username: {ds_metadata[1]}, timezone: {ds_metadata[2]}",
            inline=False
        )
    user_embed.set_footer(text=f"Portfolio Bot Data Request")
    log_channel = bot.get_channel(log_channel_id)
    if not log_channel:
        try:
            log_channel = await bot.fetch_channel(log_channel_id)
        except discord.NotFound:
            logger.error("Data log channel not found.")
            pass
    log = False
    try:
        await user.send(embed=user_embed)
    except discord.Forbidden:
        if log_channel:
            log_embed = discord.Embed(
                title="Stored Data Request",
                description=f"{user.mention} has requested their logged data.",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            log_embed.add_field(
                name="Error",
                value="The bot could not DM the user (discord.Forbidden)",
                inline=False
            )
            await log_channel.send("<@926037474805948416>", embeds=[log_embed, user_embed])
            log = True
    except Exception as e:
        if log_channel:
            log_embed = discord.Embed(
                title="Stored Data Request",
                description=f"{user.mention} has requested their logged data.",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            log_embed.add_field(
                name="Error",
                value=f"{e}",
                inline=False
            )
            log = True
            await log_channel.send("<@926037474805948416>", embeds=[log_embed, user_embed])
    if not log:
        if log_channel:
            log_embed = discord.Embed(
                title="Stored Data Request",
                description=f"{user.mention} has requested their logged data.",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await log_channel.send(embed=log_embed)
            del log
