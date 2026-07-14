import asyncio
import datetime
import discord
import sqlite3
import logging

logger = logging.getLogger(__name__)

async def Leaderboard(client):
    embed = discord.Embed(title="Leaderboard", description="", color=discord.Color.yellow())
    ctime = datetime.datetime.now()
    embed.set_footer(text=f"Updated: {ctime}")
    channel_id = 1526609024768807053
    channel = client.get_channel(channel_id)
    if not channel:
        try:
            channel = await client.fetch_channel(channel_id)
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

    # 2. If we couldn't find/fetch the message, create a new one and save it
    if not lb:
        embed = discord.Embed(title="Leaderboard", description="Loading...", color=discord.Color.yellow())
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
    await KeepUp(client, lb)
    while True:
        await asyncio.sleep(60)
        try:
            lb = await channel.fetch_message(lb.id)
            await KeepUp(client, lb)
        except discord.NotFound:
            logger.error("Leaderboard message was deleted during runtime! Breaking loop...")
            break
        except Exception as e:
            logger.error(f"Error in leaderboard loop: {e}")

async def KeepUp(client, lb):
    if not lb.embeds:
        embed = discord.Embed(title="Leaderboard", color=discord.Color.yellow())
    else:
        embed = lb.embeds[0]
    conn = sqlite3.connect("data/leaderboard.db")
    c = conn.cursor()
    c.execute("SELECT * FROM leaderboard")
    all = c.fetchall()
    all.sort(key=lambda x: x[1], reverse=True)
    description = ""
    for idx, (user_id, graded) in enumerate(all, start=1):
        try:
            user = await client.fetch_user(user_id)
            description += f"**{idx}.** - {user.mention} - {graded}\n"
        except Exception:
            description += f"**{idx}.** - *Deleted/Unknown User ({user_id})* - {graded}\n"
    embed.description = description
    embed.set_footer(text=f"Updated: {datetime.datetime.now()}")
    await lb.edit(embed=embed)