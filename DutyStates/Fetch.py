"""
Function that fetches the oldest pending duty state, extracts its data, outputs the information and images in the grading channel with the buttons. Adds 1 duty state to the grading user.
"""
import asyncio
import logging
import sqlite3
from datetime import datetime
import discord
from discord.ui import Button, View
import config
from DutyStates.DenyModal import DenyModal

logger = logging.getLogger(__name__)


async def fetch(client: discord.Client, user: discord.User):
    """
    Function that fetches the oldest pending duty state, extracts its data, outputs the information and images in the grading channel with the buttons. Adds 1 duty state to the grading user.
    :param client: The bot.
    :param user: The grading user.
    :return:
    """
    dsgrade_channel_id = config.DSGRADE_CHANNEL_ID
    gchannel = client.get_channel(dsgrade_channel_id)
    if not gchannel:
        gchannel = await client.fetch_channel(dsgrade_channel_id)
    ds_channel_id = config.DS_CHANNEL_ID
    channel = client.get_channel(ds_channel_id)
    if not channel:
        channel = await client.fetch_channel(ds_channel_id)
    while True:
        try:
            with sqlite3.connect("data/duty_states.db") as conn:
                c = conn.cursor()
                c.execute("SELECT message_id FROM pending_duties ORDER BY message_id ASC LIMIT 1")
                result = c.fetchone()
            if not result:
                nofetch = await gchannel.send("No duty state to fetch.")
                await asyncio.sleep(60)
                try:
                    await nofetch.delete()
                except discord.NotFound:
                    pass
                return
            message_id = result[0]
            try:
                message = await channel.fetch_message(message_id)
                break
            except discord.NotFound:
                logger.debug(f"Pending DS {message_id} not found.")
                with sqlite3.connect("data/duty_states.db") as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM pending_duties WHERE message_id = ?", (message_id,))
                    conn.commit()
                await gchannel.send("Oldest duty state was deleted.", delete_after=60)
                return
        except Exception as e:
            logger.error(f"Something went wrong fetching a duty state, error: {e}.", exc_info=True)
            errormessage = await gchannel.send("Something went wrong processing this duty state.")
            await asyncio.sleep(20)
            try:
                await errormessage.delete()
            except discord.NotFound:
                pass
            return
    try:
        lines = message.content.splitlines()
        start_str = lines[4].split("Time Started:")[1].strip().split()[0]
        end_str = lines[7].split("Time Ended:")[1].strip().split()[0]
        start_time = datetime.strptime(start_str, "%H:%M")
        end_time = datetime.strptime(end_str, "%H:%M")
        duration_minutes = (end_time - start_time).total_seconds() / 60
        total_mins = int(duration_minutes)
        if total_mins <= 0:
            total_mins += 1440
        hours = total_mins // 60
        minutes = total_mins % 60
        embed = discord.Embed(
            title="Duty State",
            description=f"{user.mention} \n {lines[0]} | {lines[1]} \n {lines[4]} to {lines[7]} \n Time: {hours}h {minutes}m",
            colour=discord.Colour.blue(),
        )
        embed.add_field(name="Duty", value=lines[2])
        embed.add_field(name="Start", value=lines[5][len("Tablist Started: "):].strip())
        embed.add_field(name="Ended", value=lines[8][len("Tablist Ended: "):].strip())
        if len(lines) > 9:
            embed.add_field(name="Notes: ", value=f"{lines[10]}", inline=False)
        view = View()
        accept = Button(
            label="accept",
            style=discord.ButtonStyle.green
        )
        deny = Button(
            label="deny",
            style=discord.ButtonStyle.red
        )
        fetch_msg = await gchannel.send(embed=embed)
        img1 = await gchannel.send(f"{lines[2]}")
        img2 = await gchannel.send(f"{lines[5][len('Tablist Started: '):].strip()}")
        img3 = await gchannel.send(f"{lines[8][len('Tablist Ended: '):].strip()}")

        async def accept_callback(interaction: discord.Interaction):
            """
            Calls the accept function to handle the acceptance.
            :param interaction: discord.Interaction
            """
            await accept(client, message, img1, img2, img3, interaction.user, fetch_msg, total_mins)

        accept.callback = accept_callback
        view.add_item(accept)

        async def deny_callback(interaction: discord.Interaction):
            """
            Calls the deny function to handle the denial.
            :param interaction: discord.Interaction
            """
            modal = DenyModal(client, message, img1, img2, img3, interaction.user, fetch_msg)
            await interaction.response.send_modal(modal)

        deny.callback = deny_callback
        view.add_item(deny)
        await fetch_msg.edit(view=view)
        with sqlite3.connect("data/duty_states.db") as conn:
            c = conn.cursor()
            c.execute("DELETE FROM pending_duties WHERE message_id = ?", (message_id,))
            conn.commit()
        with sqlite3.connect("data/leaderboard.db") as conn:
            c = conn.cursor()
            c.execute("SELECT graded FROM leaderboard WHERE user_id = ?", (user.id,))
            result = c.fetchone()
            if result:
                graded = result[0]
                graded += 1
                c.execute("UPDATE leaderboard SET graded = ? WHERE user_id = ?", (graded, user.id))
            else:
                c.execute("INSERT INTO leaderboard (user_id, graded) VALUES (?, ?)", (user.id, 1))
            conn.commit()

    except Exception as e:
        await gchannel.send("Something went wrong.")
        print("Something went wrong while fetching duty state message id: ", e)


'''
async def sendfetch(client, fetch):
    """
    Old function to send new fetch message after the graded duty state's debug log in the grading channel.
    :param client:
    :param fetch:
    """
    channel = client.get_channel(config.DSGRADE_CHANNEL_ID)
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
        await fetch(client, interaction.user, fetch)

    button.callback = button_callback
'''
