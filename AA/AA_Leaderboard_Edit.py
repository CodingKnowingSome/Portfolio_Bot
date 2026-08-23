"""
Called when an AA log is accepted, edits the database by adding the lessons for Staff members.
"""
import discord
import logging
import aiosqlite
from Functions.get_user_by_name import find_member_by_name
from AA.promotion_parser import parse_promotion_log

logger = logging.getLogger(__name__)


async def aa_leaderboard_edit(message: discord.Message, guild: discord.Guild):
    """
    Edits the AA leaderboard database by adding the lessons for Staff members when a log is accepted.
    Args:
        message: The log message as a discord.Message.
        guild: The server as discord.Guild.
    """
    try:

        names = parse_promotion_log(message.content)

        if names:
            found_user = []
            for name in names.lessons:
                member = find_member_by_name(guild, name)

                if member:
                    found_user.append(member)
                else:
                    pass
        else:
            found_user = []

        if found_user:
            async with aiosqlite.connect("data/leaderboard.db") as conn:
                for user in found_user:
                    async with conn.execute("SELECT lessons, total FROM aa_leaderboard WHERE user_id = ?", (user.id,)) as c:
                        result = await c.fetchone()
                    if result:
                        lessons = result[0]
                        lessons += 1
                        total = result[1]
                        total += 1
                        await conn.execute("UPDATE aa_leaderboard SET lessons = ? WHERE user_id = ?", (lessons, user.id))
                        await conn.execute("UPDATE aa_leaderboard SET total = ? WHERE user_id = ?", (total, user.id))
                    else:
                        await conn.execute("INSERT INTO aa_leaderboard (user_id, lessons, total) VALUES (?, ?, ?)",
                                  (user.id, 1, 1))
                    await conn.commit()
        else:
            pass
    except Exception as e:
        logger.error(f"Failed to edit the AA Leaderboard database: {e}")
