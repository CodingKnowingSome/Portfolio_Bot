import discord
from datetime import datetime
import sqlite3
import logging

logger = logging.getLogger(__name__)

async def Deny(client, message, img1, img2, img3, user, fetch_msg, reason):
    ds_channel_id = 1526379960179232818
    ds_channel = client.get_channel(ds_channel_id)
    gchannel_id = 1526383804464365628
    gchannel = client.get_channel(gchannel_id)
    embed = discord.Embed(
        title="Denied",
        description=f"{message.author.mention} your duty state has been denied by {user.mention}",
        color=discord.Color.red()
    )

    embed.add_field(name="Reason: ", value=reason)
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embed.set_footer(text=f"{currenttime}")
    await message.reply(embed=embed)
    await message.clear_reactions()
    await message.add_reaction("❌")
    embed = fetch_msg.embeds[0]
    embed.color = discord.Color.red()
    embed.set_footer(text=f"Denied! | {reason}")
    await fetch_msg.edit(embed=embed, view=None)
    await fetch_msg.delete()
    try:
        await img1.delete()
        await img2.delete()
        await img3.delete()
    except Exception as e:
        await gchannel.send("Could not delete the embed images!")
        print(f"Could not delete the embed images! {img1.id} | {img2.id} | {img3.id}", e)