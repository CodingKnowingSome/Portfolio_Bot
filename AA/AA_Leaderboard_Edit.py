"""
Called when an AA log is accepted, edits the database by adding the lessons for Staff members.
"""
import discord
import logging
import aiosqlite
from Functions.get_user_by_name import find_member_by_name
from AA.promotion_parser import parse_promotion_log

logger = logging.getLogger(__name__)


async def aa_leaderboard_edit(client, message: discord.Message, guild: discord.Guild):
    """
    Edits the AA leaderboard database by adding the lessons for Staff members when a log is accepted.
    Args:
        client: The bot.
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
                    await conn.execute("""
                        INSERT INTO aa_leaderboard (user_id, lessons, total)
                        VALUES (?, 1, 1)
                        ON CONFLICT (user_id) DO UPDATE SET
                            lessons = lessons + 1,
                            total = total + 1
                    """, (user.id,))
                    await conn.commit()

        else:
            pass
        client.dispatch("leaderboard_update", "aa")
    except Exception as e:
        logger.error(f"Failed to edit the AA Leaderboard database: {e}")
