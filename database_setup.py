"""
Sets up the required databases for the bot to function.
"""
import aiosqlite
import logging

logger = logging.getLogger(__name__)


async def database_setup():
    """
    Sets up the required databases for the bot to function.
    """
    async with aiosqlite.connect("data/duty_states.db") as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS pending_duties (
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (message_id, user_id)
        ) 
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS fetches (
            officer_id INTEGER NOT NULL PRIMARY KEY,
            message_id INTEGER NOT NULL
        )
        """)
        await conn.commit()

    async with aiosqlite.connect("data/leaderboard.db") as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            user_id INTEGER NOT NULL PRIMARY KEY,
            graded INTEGER NOT NULL DEFAULT 0,
            total INTEGER NOT NULL DEFAULT 0
        )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard_meta (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        """)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS aa_leaderboard_meta (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS aa_leaderboard (
            user_id INTEGER NOT NULL PRIMARY KEY,
            lessons INTEGER NOT NULL DEFAULT 0,
            total INTEGER NOT NULL DEFAULT 0
        )
        """)
        await conn.commit()

    async with aiosqlite.connect("data/ds_metadata.db") as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS ds_metadata (
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            timezone TEXT NOT NULL,
            PRIMARY KEY (user_id)
        )
        """)
        await conn.commit()
