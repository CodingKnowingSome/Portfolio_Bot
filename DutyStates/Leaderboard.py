"""
Creates, updates, and upkeep's the leaderboard.
"""
import datetime
import discord
import aiosqlite
import logging
import config
from Functions.cache_members import get_member

logger = logging.getLogger(__name__)


async def leaderboard(client: discord.Client):
    """
    Creates and edits the leaderboard, start the upkeep process.
    Args:
        client: The bot.

    Returns: NA

    """
    ld_channel_id = config.LD_CHANNEL_ID
    channel = client.get_channel(ld_channel_id)
    if not channel:
        try:
            channel = await client.fetch_channel(ld_channel_id)
        except Exception as e:
            logger.error(f"Failed to fetch leaderboard channel: {e}")
            return
    async with aiosqlite.connect("data/leaderboard.db") as conn:
        async with conn.execute("SELECT value FROM leaderboard_meta WHERE key = 'message_id'") as c:
            row = await c.fetchone()

    lb = None

    if row:
        saved_msg_id = row[0]
        try:
            lb = await channel.fetch_message(saved_msg_id)
        except discord.NotFound:
            logger.warning("Saved leaderboard message was deleted. We will make a new one.")
        except Exception as e:
            logger.error(f"Error fetching leaderboard: {e}")

    if not lb:
        embed = discord.Embed(title="Leaderboard", description="Loading...", color=discord.Color.yellow())
        embed.set_thumbnail(url="https://www.citypng.com/photo/20680/hd-python-logo-symbol-transparent-png")
        lb = await channel.send(embed=embed)

        async with aiosqlite.connect("data/leaderboard.db") as conn:
            await conn.execute("""
                INSERT OR REPLACE INTO leaderboard_meta (key, value) 
                VALUES ('message_id', ?)
            """, (lb.id,))
            await conn.commit()
    await officer_keepup(client, lb)


async def officer_keepup(client: discord.Client, lb: discord.Message):
    """
    Fetches Officers from the database, orders them, creates the new embed and updates the leaderboard.
    Args:
        client: The bot.
        lb: The leaderboard as a discord.Message.

    Returns: NA

    """
    if not lb.embeds:
        embed = discord.Embed(title="Leaderboard", color=discord.Color.yellow())
        embed.set_thumbnail(
            url="https://www.citypng.com/public/uploads/preview/hd-python-logo-symbol-transparent-png-735811696257415dbkifcuokn.png")
    else:
        embed = lb.embeds[0]
    guild = client.get_guild(config.TEST_GUILD_ID)
    if not guild:
        try:
            guild = await client.fetch_guild(config.TEST_GUILD_ID)
        except Exception as e:
            logger.error(f"Failed to fetch guild: {e}")
            return
    async with aiosqlite.connect("data/leaderboard.db") as conn:
        async with conn.execute("SELECT * FROM leaderboard") as c:
            all_officer = await c.fetchall()
    processed_officers = []
    for user_id, graded, total in all_officer:
        user = await get_member(guild, user_id)
        has_in_role = False
        if user:
            has_in_role = user.get_role(config.IN_ROLE_ID) is not None
            user_display = user.nick
            user_name = user_display.split("|")[0].strip()
        else:
            user_name = f"*Deleted/Unknown User*"
        is_inactive = 1 if has_in_role else 0
        processed_officers.append((is_inactive, graded or 0, total or 0, user_name, has_in_role))
    processed_officers.sort(key=lambda x: (x[0], -x[1]))
    lines = [
        "Leaderboard for weekly and all time graded duty states of current Officers.",
        "",
        "```",
        f"{'#':<3} {'Staff':<15} {'Week':<8} {'All-time':<5}",
        "----------------------------------"
    ]
    for idx, (is_inactive, graded, total, user_name, has_in_role) in enumerate(processed_officers, start=1):
        week_val = "⛔" if has_in_role else str(graded)
        display_name = user_name[:15] if len(user_name) > 15 else user_name
        lines.append(f"{idx:<3} {display_name:<15} {week_val:<8} {total:<5}")
    lines.append("```")
    ctime = int(datetime.datetime.now().timestamp())
    lines.append(f"-# Last updated: <t:{ctime}:T>")
    embed.description = "\n".join(lines)
    embed.set_thumbnail(
        url="https://www.citypng.com/public/uploads/preview/hd-python-logo-symbol-transparent-png-735811696257415dbkifcuokn.png")
    await lb.edit(embed=embed)
