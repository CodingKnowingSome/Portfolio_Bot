import discord
from datetime import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)

async def Accept(client, message, img1, img2, img3, user, fetch_msg, total_mins):
    ds_channel_id = 1526379960179232818
    ds_channel = client.get_channel(ds_channel_id)
    gchannel_id = 1526383804464365628
    gchannel = client.get_channel(gchannel_id)

    points = None

    def points_check(total_mins: int) -> int:
        if total_mins < 2*60:
            return 1
        elif total_mins < 4*60:
            return 2
        elif total_mins < 6*60:
            return 3
        elif total_mins < 8*60:
            return 4
        elif total_mins < 10*60:
            return 5
        elif total_mins < 15*60:
            return 6
        elif total_mins < 20*60:
            return 7
        elif total_mins < 24*60:
            return 8
        else:
            return 9

    points = points_check(total_mins)

    embed = discord.Embed(
        title="Accepted",
        description=f"{message.author.mention} your duty state has been accepted by {user.mention}. You have earned {points} point(s).",
        color=discord.Color.green()
    )

    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed.set_footer(text=f"{currenttime}")
    await message.reply(embed=embed)
    await message.clear_reactions()
    await message.add_reaction("✔️")
    await fetch_msg.delete()
    try:
        await img1.delete()
        await img2.delete()
        await img3.delete()
    except Exception as e:
        await gchannel.send("Could not delete the embed images!")
        print(f"Could not delete the embed images! {img1.id} | {img2.id} | {img3.id}", e)
