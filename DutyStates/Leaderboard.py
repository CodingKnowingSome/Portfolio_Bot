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


async def leaderboard(client: discord.Client):
    """
    Creates and updates the leaderboard.
    :param client: The bot.
    :return:
    """
    embed = discord.Embed(title="leaderboard", description="", color=discord.Color.yellow())
    ctime = datetime.datetime.now()
    embed.set_footer(text=f"Updated: {ctime}")
    ld_channel_id = config.LD_CHANNEL_ID
    channel = client.get_channel(ld_channel_id)
    if not channel:
        try:
            channel = await client.fetch_channel(ld_channel_id)
        except Exception as e:
            logger.error(f"Failed to fetch leaderboard channel: {e}")
            return
    conn = sqlite3.connect("data/leaderboard.db")
    c = conn.cursor()
    c.execute("SELECT value FROM leaderboard_meta WHERE key = 'message_id'")
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
        embed = discord.Embed(title="leaderboard", description="Loading...", color=discord.Color.yellow())
        embed.set_footer(text=f"Updated: {datetime.datetime.now()}")
        lb = await channel.send(embed=embed)

        conn = sqlite3.connect("data/leaderboard.db")
        c = conn.cursor()
        c.execute("""
            INSERT OR REPLACE INTO leaderboard_meta (key, value) 
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
        except discord.HTTPException as e:
            logger.warning(f"Network issue while updating leaderboard (HTTP {e.status}): Retrying next cycle.")
        except Exception as e:
            logger.error(f"Error in leaderboard loop: {e}")


async def keepup(client: discord.Client, lb: discord.Message):
    """
    Keeps up the leaderboard.
    :param client:
    :param lb:
    """
    if not lb.embeds:
        embed = discord.Embed(title="leaderboard", color=discord.Color.yellow())
    else:
        embed = lb.embeds[0]
    conn = sqlite3.connect("data/leaderboard.db")
    c = conn.cursor()
    c.execute("SELECT * FROM leaderboard")
    all_officer = c.fetchall()
    all_officer.sort(key=lambda x: x[1], reverse=True)
    description = ""
    for idx, (user_id, graded) in enumerate(all_officer, start=1):
        user = client.get_user(user_id)
        if not user:
            try:
                user = await client.fetch_user(user_id)
            except Exception:
                user = None
        if user:
            description += f"**{idx}.** - {user.mention} - {graded}\n"
        else:
            description += f"**{idx}.** - *Deleted/Unknown User ({user_id})* - {graded}\n"
    embed.description = description
    if not description:
        embed.description = "NA"
    embed.set_footer(text=f"Updated: {datetime.datetime.now()}")
    await lb.edit(embed=embed)
