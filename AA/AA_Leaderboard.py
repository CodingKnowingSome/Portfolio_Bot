"""
Creates, updates, and upkeep's the leaderboard.
"""
import asyncio
import datetime
import discord
import sqlite3
import logging
import config

logger = logging.getLogger(__name__)


async def aaleaderboard(client: discord.Client):
    """
    Creates and edits the leaderboard, start the upkeep process.
    Args:
        client: The bot.

    Returns: NA

    """
    embed = discord.Embed(title="Leaderboard", description="", color=discord.Color.yellow())
    ctime = datetime.datetime.now()
    embed.set_footer(text=f"Updated: {ctime}")
    ld_channel_id = config.AA_LD_CHANNEL_ID
    channel = client.get_channel(ld_channel_id)
    if not channel:
        try:
            channel = await client.fetch_channel(ld_channel_id)
        except Exception as e:
            logger.error(f"Failed to fetch leaderboard channel: {e}")
            return
    conn = sqlite3.connect("data/leaderboard.db")
    c = conn.cursor()
    c.execute("SELECT value FROM aa_leaderboard_meta WHERE key = 'message_id'")
    row = c.fetchone()
    conn.close()

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
        embed.set_footer(text=f"Updated: {datetime.datetime.now()}")
        lb = await channel.send(embed=embed)

        conn = sqlite3.connect("data/leaderboard.db")
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO aa_leaderboard_meta (key, value) 
            VALUES ('message_id', ?)
        """, (lb.id,))
        conn.commit()
        conn.close()
    await keepup(client, lb)
    while True:
        await asyncio.sleep(60)
        try:
            await keepup(client, lb)
        except discord.NotFound:
            logger.error("leaderboard message was deleted during runtime! Breaking loop...")
            break
        except Exception as e:
            logger.error(f"Error in leaderboard loop: {e}")


async def keepup(client: discord.Client, lb: discord.Message):
    """
    Fetches Officers from the database, orders them, creates the new embed and updates the leaderboard.
    Args:
        client: The bot.
        lb: The leaderboard as a discord.Message.

    Returns: NA

    """
    if not lb.embeds:
        embed = discord.Embed(title="Leaderboard", color=discord.Color.yellow())
    else:
        embed = lb.embeds[0]
    guild = client.get_guild(config.TEST_GUILD_ID)
    if not guild:
        try:
            guild = await client.fetch_guild(config.TEST_GUILD_ID)
        except Exception as e:
            logger.error(f"Could not fetch guild: {e}.")
            return
    conn = sqlite3.connect("data/leaderboard.db")
    c = conn.cursor()
    c.execute("SELECT * FROM aa_leaderboard")
    all_staff = c.fetchall()
    conn.close()
    processed_staff = []
    for user_id, lessons, total in all_staff:
        user = guild.get_member(user_id)
        if not user:
            try:
                user = await guild.fetch_member(user_id)
            except Exception as e:
                user = None
                logger.warning(f"Failed to fetch member {user_id}: {e}")
        has_in_role = False
        if user:
            has_in_role = user.get_role(config.IN_ROLE_ID) is not None
            user_display = user.nick
            user_name = user_display.split("|")[0].strip()
        else:
            user_name = f"*Deleted/Unknown User ({user_id})*"
        is_inactive = 1 if has_in_role else 0
        processed_staff.append((
            is_inactive,
            lessons or 0,
            total or 0,
            user_name,
            has_in_role
        ))
    processed_staff.sort(key=lambda x: (x[0], -x[1]))
    description = ""
    for idx, (is_inactive, lessons, total, user_name, has_in_role) in enumerate(processed_staff, start=1):
        if not has_in_role:
            description += f"**{idx}.** - {user_name} - {lessons} ({total})\n"
        else:
            description += f"**{idx}.** - {user_name} - ⛔ ({total})\n"
    embed.description = description if description else "NA"
    embed.set_footer(text=f"Updated: {datetime.datetime.now()}")
    await lb.edit(embed=embed)