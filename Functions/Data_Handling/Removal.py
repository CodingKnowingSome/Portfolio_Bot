"""
Handles data removal requests.
"""
import discord
import logging
import config
from datetime import datetime
from Functions.get_roblox_id import get_roblox_id
import sqlite3

logger = logging.getLogger(__name__)


async def removal(bot: discord.Client, user: discord.User, username: str = None):
    """
    Handles the data removal requests. Deletes data, informs the user, and sends them the kept KoS and blacklist data.
    Args:
        bot: The bot as discord.Client.
        user: The user using the command as discord.User.
        username: The username of the user using the command as str.
    """
    log_channel_id = config.DATA_LOG_CHANNEL_ID
    discord_id = user.id
    roblox_id, exact_username = get_roblox_id(username)

    if roblox_id:
        with sqlite3.connect("data/kos_blacklist.db") as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM kos WHERE user_id = ?", (roblox_id,))
            kos_row = c.fetchone()
            c.execute("SELECT * FROM blacklist WHERE user_id = ?", (roblox_id,))
            blacklist = c.fetchone()
    pending_duties_del = 0
    with sqlite3.connect("data/duty_states.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM pending_duties WHERE user_id = ?", (discord_id,))
        pending_duties_del = c.rowcount
        conn.commit()
    leaderboard_del = 0
    aa_leaderboard_del = 0
    with sqlite3.connect("data/leaderboard.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM leaderboard WHERE user_id = ?", (discord_id,))
        leaderboard_del = c.rowcount
        c.execute("DELETE FROM aa_leaderboard WHERE user_id = ?", (discord_id,))
        aa_leaderboard_del = c.rowcount
        conn.commit()
    with sqlite3.connect("data/ds_metadata.db") as conn:
        c = conn.cursor()
        c.execute("DELETE FROM ds_metadata WHERE user_id = ?", (discord_id,))
        ds_metadata_del = c.rowcount
        conn.commit()
    user_embed = discord.Embed(
        title="Portfolio Bot Data Removal",
        color=discord.Color.red(),
        timestamp=datetime.now(),
        description="As of you request, your personal data (excluding moderation as of ToS) has been deleted from the bot. Below is a summary of the kept and deleted data."
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
            name="KoS Information (Kept)",
            value=f"ID: {kos_row[0]}, status: {kos_row[1]}",
            inline=False
        )
    if blacklist:
        user_embed.add_field(
            name="Blacklist Information (Kept)",
            value=f"ID: {blacklist[0]}, reason: {blacklist[1]}, last edited: {blacklist[3]}",
            inline=False
        )
    del_info = ""
    if pending_duties_del != 0:
        del_info += f"Pending Duties: {pending_duties_del}\n"
    if aa_leaderboard_del != 0:
        del_info += f"AA Leaderboard: {aa_leaderboard_del}\n"
    if leaderboard_del != 0:
        del_info += f"Leaderboard: {leaderboard_del}\n"
    if ds_metadata_del != 0:
        del_info += f"DS Metadata: {ds_metadata_del}\n"
    user_embed.add_field(
        name="Deleted Information Entries",
        value=del_info,
        inline=False
    )
    user_embed.set_footer(text=f"Portfolio Bot Data Removal Request")
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
                description=f"{user.mention} has requested to delete their logged data.",
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
                title="Stored Data Removal Request",
                description=f"{user.mention} has requested to delete their logged data.",
                color=discord.Color.red(),
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
                description=f"{user.mention} has requested to delete their logged data.",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await log_channel.send(embed=log_embed)
            del log
