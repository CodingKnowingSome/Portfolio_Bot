"""
Fetches the oldest duty state.
"""
import asyncio
import logging
import aiosqlite
from datetime import datetime
import discord
from discord.ui import Button, View
import config
from DutyStates.DenyModal import DenyModal
from DutyStates.Accept import accept

logger = logging.getLogger(__name__)


async def fetch(client: discord.Client, user: discord.User, interaction: discord.Interaction):
    """
    Fetches the oldest duty state, outputs the basic info, the three images with an accept and deny button.
    Args:
        interaction: The interaction object from discord.Interaction
        client: The bot.
        user: The grading user as discord.User.

    Returns: NA

    """
    await interaction.response.defer()
    dsgrade_channel_id = config.DSGRADE_CHANNEL_ID
    gchannel = client.get_channel(dsgrade_channel_id)
    if not gchannel:
        gchannel = await client.fetch_channel(dsgrade_channel_id)
    ds_channel_id = config.DS_CHANNEL_ID
    channel = client.get_channel(ds_channel_id)
    if not channel:
        channel = await client.fetch_channel(ds_channel_id)
    officer_id = interaction.user.id
    while True:
        try:
            async with aiosqlite.connect("data/duty_states.db") as conn:
                async with conn.execute("SELECT message_id FROM fetches WHERE officer_id = ?", (officer_id,)) as c:
                    existing_claim = await c.fetchone()
                if existing_claim:
                    message_id = existing_claim[0]
                else:
                    async with conn.execute("""
                    SELECT message_id FROM pending_duties
                    WHERE message_id NOT IN (SELECT message_id FROM fetches)
                    ORDER BY message_id ASC LIMIT 1
                    """) as c:
                        result = await c.fetchone()
                    if not result:
                        nofetch = await interaction.followup.send("No duty state to fetch.", ephemeral=True)
                        await asyncio.sleep(60)
                        try:
                            await nofetch.delete()
                        except discord.NotFound:
                            pass
                        return
                    message_id = result[0]
                    await conn.execute("INSERT INTO fetches VALUES (?, ?)", (officer_id, message_id))
                    await conn.commit()
                try:
                    message = await channel.fetch_message(message_id)
                    break
                except discord.NotFound:
                    logger.debug(f"Pending DS {message_id} not found.")
                    async with aiosqlite.connect("data/duty_states.db") as conn:
                        await conn.execute("DELETE FROM pending_duties WHERE message_id = ?", (message_id,))
                        await conn.execute("DELETE FROM fetches WHERE message_id = ?", (message_id,))
                        await conn.commit()
                    continue
        except Exception as e:
            logger.error(f"Something went wrong fetching a duty state, error: {e}.", exc_info=True)
            errormessage = await interaction.followup.send("Something went wrong processing this duty state.",
                                                           ephemeral=True)
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
            description=f"{user.mention} \n {lines[0]} | {lines[1]}\nTime: {hours}h {minutes}m ({lines[4][len("Time Started: "):].strip()} to {lines[7][len("Time Ended: "):].strip()})",
            colour=discord.Colour.blue(),
        )
        embed.add_field(name="Duty", value=lines[2])
        embed.add_field(name="Start", value=lines[5][len("Tablist Started: "):].strip())
        embed.add_field(name="Ended", value=lines[8][len("Tablist Ended: "):].strip())
        if len(lines) > 9:
            embed.add_field(name="Notes: ", value=f"{lines[10]}", inline=False)
        view = View(timeout=None)
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

        async def accept_callback(interaction_: discord.Interaction):
            """
            Accept button callback, calls the accept function to handle the acceptance.
            Args:
                interaction_: The interaction object from discord.Interaction.
            """
            await accept(client, message, interaction_.user, total_mins, interaction_)

        accept_button.callback = accept_callback
        view.add_item(accept_button)

        async def deny_callback(interaction_: discord.Interaction):
            """
            Deny button callback, calls the deny function to handle the denial.
            Args:
                interaction_: The interaction object from discord.Interaction.
            """
            modal = DenyModal(client, message, interaction_.user)
            await interaction_.response.send_modal(modal)

        deny_button.callback = deny_callback
        view.add_item(deny_button)
        await interaction.followup.send(embed=embed, view=view, ephemeral=True)
        await interaction.original_response()
        await interaction.followup.send(f"{lines[2]}", ephemeral=True)
        await interaction.followup.send(f"{lines[5][len('Tablist Started: '):].strip()}", ephemeral=True)
        await interaction.followup.send(f"{lines[8][len('Tablist Ended: '):].strip()}", ephemeral=True)
        async with aiosqlite.connect("data/duty_states.db") as conn:
            await conn.execute("DELETE FROM pending_duties WHERE message_id = ?", (message_id,))
            await conn.commit()

    except Exception as e:
        await gchannel.send("Something went wrong.")
        print("Something went wrong while fetching duty state message id: ", e)
