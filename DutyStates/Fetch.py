"""
Fetches the oldest duty state.
"""
import asyncio
import logging
import sqlite3
from datetime import datetime
import discord
from discord.ui import Button, View
import config
from DutyStates.DenyModal import DenyModal
from DutyStates.Accept import accept

logger = logging.getLogger(__name__)


async def fetch(client: discord.Client, user: discord.User):
    """
    Fetches the oldest duty state, outputs the basic info, the three images with an accept and deny button.
    Args:
        client: The bot.
        user: The grading user as discord.User.

    Returns: NA

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
        # noinspection PyTypeChecker
        accept_button = Button(
            label="Accept",
            style=discord.ButtonStyle.green
        )
        # noinspection PyTypeChecker
        deny_button = Button(
            label="Deny",
            style=discord.ButtonStyle.red
        )
        fetch_msg = await gchannel.send(embed=embed)
        img1 = await gchannel.send(f"{lines[2]}")
        img2 = await gchannel.send(f"{lines[5][len('Tablist Started: '):].strip()}")
        img3 = await gchannel.send(f"{lines[8][len('Tablist Ended: '):].strip()}")

        async def accept_callback(interaction: discord.Interaction):
            """
            Accept button callback, calls the accept function to handle the acceptance.
            Args:
                interaction: The interaction object from discord.Interaction.
            """
            await accept(client, message, img1, img2, img3, interaction.user, fetch_msg, total_mins)

        accept_button.callback = accept_callback
        view.add_item(accept_button)

        async def deny_callback(interaction: discord.Interaction):
            """
            Deny button callback, calls the deny function to handle the denial.
            Args:
                interaction: The interaction object from discord.Interaction.
            """
            modal = DenyModal(client, message, img1, img2, img3, interaction.user, fetch_msg)
            await interaction.response.send_modal(modal)

        deny_button.callback = deny_callback
        view.add_item(deny_button)
        await fetch_msg.edit(view=view)
        with sqlite3.connect("data/duty_states.db") as conn:
            c = conn.cursor()
            c.execute("DELETE FROM pending_duties WHERE message_id = ?", (message_id,))
            conn.commit()
        with sqlite3.connect("data/leaderboard.db") as conn:
            c = conn.cursor()
            c.execute("SELECT graded, total FROM leaderboard WHERE user_id = ?", (user.id,))
            result = c.fetchone()
            if result:
                graded = result[0]
                graded += 1
                total = result[1]
                total += 1
                c.execute("UPDATE leaderboard SET graded = ? WHERE user_id = ?", (graded, user.id))
                c.execute("UPDATE leaderboard SET total = ? WHERE user_id = ?", (total, user.id))
            else:
                c.execute("INSERT INTO leaderboard (user_id, graded, total) VALUES (?, ?, ?)", (user.id, 1, 1))
            conn.commit()

    except Exception as e:
        await gchannel.send("Something went wrong.")
        print("Something went wrong while fetching duty state message id: ", e)
