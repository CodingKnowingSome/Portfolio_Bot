"""
Sets up the required databases for the bot to function.
"""
import sqlite3
import logging

logger = logging.getLogger(__name__)


async def database_setup():
    """
    Sets up the required databases for the bot to function.
    """
    conn = sqlite3.connect("data/duty_states.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS pending_duties (
        message_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (message_id, user_id)
    ) 
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect("data/leaderboard.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS leaderboard (
        user_id INTEGER NOT NULL,
        graded INTEGER NOT NULL
    )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard_meta (
            key TEXT PRIMARY KEY,
            value INTEGER
        )
    """)
    conn.commit()
    conn.close()

    conn = sqlite3.connect("data/ds_metadata.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS ds_metadata (
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        timezone NOT NULL,
        PRIMARY KEY (user_id, username)
    )
    """)
    conn.commit()
    conn.close()
