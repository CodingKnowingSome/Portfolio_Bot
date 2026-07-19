import asyncio
from datetime import datetime
import sqlite3
import discord
from discord.ui import Button, View
from DutyStates.Accept import Accept
from DutyStates.DenyModal import DenyModal
import logging

logger = logging.getLogger(__name__)

async def Fetch(client, user, fetch):
    gchannel_id = 1526383804464365628
    gchannel = client.get_channel(gchannel_id)
    if not gchannel:
        gchannel = await client.fetch_channel(gchannel_id)
    try:
        conn = sqlite3.connect("data/duty_states.db")
        c = conn.cursor()
        c.execute("SELECT message_id FROM pending_duties ORDER BY message_id ASC LIMIT 1")
        result = c.fetchone()
        if not result:
            nofetch = await gchannel.send("No duty state to fetch.", delete_after=60)
            await asyncio.sleep(60)
            await nofetch.delete()
            return
        message_id = result[0]
        channel_id = 1526379960179232818
        channel = client.get_channel(channel_id)
        if not channel:
            channel = await client.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)
        lines = message.content.splitlines()
        start_str = lines[4].split("Time Started:")[1].strip().split()[0]
        end_str = lines[7].split("Time Ended:")[1].strip().split()[0]
        start_time = datetime.strptime(start_str, "%H:%M")
        end_time = datetime.strptime(end_str, "%H:%M")
        duration_minutes = (end_time - start_time).total_seconds() / 60
        total_mins = int(duration_minutes)
        hours = total_mins // 60
        minutes = total_mins % 60
        embed = discord.Embed(
            title="Duty State",
            description=f"{user.mention} \n {lines[0]} | {lines[1]} \n {lines[4]} to {lines[7]} \n Time: {hours}h {minutes}m",
            colour=discord.Colour.blue(),
        )
        embed.add_field(name="Duty", value=lines[2], inline=True)
        embed.add_field(name="Start", value=lines[5][len("Tablist Started: "):].strip(), inline=True)
        embed.add_field(name="Ended", value=lines[8][len("Tablist Ended: "):].strip(), inline=True)
        if len(lines) > 9:
            embed.add_field(name="Notes: ", value=f"{lines[10]}", inline=False)
        view = View()
        accept = Button(
            label="Accept",
            style=discord.ButtonStyle.green
        )
        deny = Button(
            label="Deny",
            style=discord.ButtonStyle.red
        )
        fetch_msg = await gchannel.send(embed=embed)
        img1 = await gchannel.send(f"{lines[2]}")
        img2 = await gchannel.send(f"{lines[5][len('Tablist Started: '):].strip()}")
        img3 = await gchannel.send(f"{lines[8][len('Tablist Ended: '):].strip()}")
        async def accept_callback(interaction):
            await Accept(client, message, img1, img2, img3, interaction.user, fetch_msg, total_mins)
        accept.callback=accept_callback
        view.add_item(accept)
        async def deny_callback(interaction):
            modal = DenyModal(client, message, img1, img2, img3, interaction.user, fetch_msg)
            await interaction.response.send_modal(modal)
        deny.callback=deny_callback
        view.add_item(deny)
        await fetch_msg.edit(view=view)
        c.execute("DELETE FROM pending_duties WHERE message_id = ?", (message_id,))
        conn.commit()
        conn = sqlite3.connect("data/leaderboard.db")
        c = conn.cursor()
        c.execute("SELECT graded FROM leaderboard WHERE user_id = ?", (user.id,))
        result = c.fetchone()
        if result:
            graded = result[0]
            graded = graded + 1
            c.execute("UPDATE leaderboard SET graded = ? WHERE user_id = ?", (graded, user.id))
        else:
            c.execute("INSERT INTO leaderboard (user_id, graded) VALUES (?, ?)", (user.id, 1))
        conn.commit()
        conn.close()

    except Exception as e:
        await gchannel.send("Something went wrong.")
        print("Something went wrong while fetching duty state message id: ", e)


async def SendFetch(client, fetch):
    channel = client.get_channel(1526383804464365628)
    embed = discord.Embed(
        title="Fetch a duty state!",
        color=discord.Color.blue()
    )
    button = Button(label="Fetch a duty state!", style=discord.ButtonStyle.primary)
    await fetch.delete()
    view = View()
    view.add_item(button)
    fetch = await channel.send(embed=embed, view=view)
    async def button_callback(interaction: discord.Interaction):
        await Fetch(client, interaction.user, fetch)
    button.callback = button_callback