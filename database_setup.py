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
    with sqlite3.connect("data/duty_states.db") as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS pending_duties (
            message_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (message_id, user_id)
        ) 
        """)
        conn.commit()

    with sqlite3.connect("data/leaderboard.db") as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            user_id INTEGER NOT NULL PRIMARY KEY,
            graded INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0
        )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard_meta (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS aa_leaderboard_meta (
                key TEXT PRIMARY KEY,
                value INTEGER
            )
        """)
        c.execute("""
        CREATE TABLE IF NOT EXISTS aa_leaderboard (
            user_id INTEGER NOT NULL PRIMARY KEY,
            lessons INTEGER DEFAULT 0,
            total INTEGER DEFAULT 0
        )
        """)
        conn.commit()

    with sqlite3.connect("data/ds_metadata.db") as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS ds_metadata (
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            timezone TEXT NOT NULL,
            PRIMARY KEY (user_id, username)
        )
        """)
        conn.commit()

    with sqlite3.connect("data/keys.db") as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS keys (
            public TEXT NOT NULL,
            user_id INTEGER NOT NULL PRIMARY KEY
        )
        """)
        conn.commit()
