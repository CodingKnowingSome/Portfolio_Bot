"""
Called when an AA log is accepted, edits the database by adding the lessons for Staff members.
"""
import discord
import logging
import sqlite3
from Functions.get_user_by_name import find_member_by_name

logger = logging.getLogger(__name__)


async def aa_leaderboard_edit(message: discord.Message, guild: discord.Guild):
    """
    Edits the AA leaderboard database by adding the lessons for Staff members when a log is accepted.
    Args:
        message: The log message as a discord.Message.
        guild: The server as discord.Guild.
    """
    try:

        lines = message.content.splitlines()
        line_12 = lines[12]
        start_index = line_12.index("username:") + len("username:")
        end_index = line_12.index("action:")

        names = line_12[start_index:end_index].strip()

        if names.strip():
            names_list = names.split(" ")
            found_user = []
            for name in names_list:
                member = find_member_by_name(guild, name)

                if member:
                    found_user.append(member)
                else:
                    pass
        else:
            found_user = []

        if found_user:
            with sqlite3.connect("data/leaderboard.db") as conn:
                for user in found_user:
                    c = conn.cursor()
                    c.execute("SELECT lessons, total FROM aa_leaderboard WHERE user_id = ?", (user.id,))
                    result = c.fetchone()
                    if result:
                        lessons = result[0]
                        lessons += 1
                        total = result[1]
                        total += 1
                        c.execute("UPDATE aa_leaderboard SET lessons = ? WHERE user_id = ?", (lessons, user.id))
                        c.execute("UPDATE aa_leaderboard SET total = ? WHERE user_id = ?", (total, user.id))
                    else:
                        c.execute("INSERT INTO aa_leaderboard (user_id, lessons, total) VALUES (?, ?, ?)",
                                  (user.id, 1, 1))
                    conn.commit()
        else:
            pass
    except Exception as e:
        logger.error(f"Failed to edit the AA Leaderboard database: {e}")
