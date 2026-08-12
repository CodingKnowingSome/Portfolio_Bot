"""
Checks if the message sent in the duty state channel follows the correct format.
"""
import discord
from urllib.parse import urlparse
from datetime import datetime
import re
import sqlite3
import logging

logger = logging.getLogger(__name__)


async def dutylistener(message: discord.Message):
    """
    Checks if a message sent in the duty state channel follows the correct format, if so it adds it to the pending
    duty states and notifies the user, otherwise it notifies the user of the first error.
    #TODO: The error should contain everything wrong with the submission.
    Args:
        message: The duty state message as discord.Message.

    Returns: NA

    """
    try:
        lines = message.content.splitlines()
        if len(lines) > 0:
            if lines[0].startswith("Username: ") and len(lines[0][len("Username: "):].strip()) > 0:
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 1 should be: 'Username: CodingKnowingSome'",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 1 should be: 'Username: CodingKnowingSome'",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if len(lines) > 1:
            if lines[1].startswith("Duty: ") and len(lines[1][len("Duty: "):].strip()) > 0:
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 2 should be: 'Duty: xxx'",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 2 should be: 'Duty: xxx'",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if len(lines) > 2:
            parsed = urlparse(lines[2])
            if parsed.scheme == "https" and parsed.netloc:
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 3 should start contain your duty post screenshot link.",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 3 should start contain your duty post screenshot link.",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if len(lines) > 3:
            if not lines[3].strip():
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 4 should be an empty line!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 4 should be an empty line!",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if len(lines) > 4:
            prefix = "Time Started: "
            time_format = r"^\d{2}:\d{2} GMT[+-]\d+$"
            if lines[4].startswith(prefix) and re.match(time_format, lines[4][len(prefix):].strip()):
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 5 should follow this format:\nTime Started: 12:00 GMT+1",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 5 should follow this format:\nTime Started: 12:00 GMT+1",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if len(lines) > 5:
            prefix = "Tablist Started: "
            if lines[5].startswith(prefix) and re.match(r"^https://\S+$", lines[5][len(prefix):].strip()):
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 6 should follow the format:\nTablist Started: https://tablist.org/xxx",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 6 should follow the format:\nTablist Started: https://tablist.org/xxx",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")

            return
        if len(lines) > 6:
            if not lines[6].strip():
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 7 should be an empty line!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 7 should be an empty line!",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if len(lines) > 7:
            prefix = "Time Ended: "
            time_format = r"^\d{2}:\d{2} GMT[+-]\d+$"
            if lines[7].startswith(prefix) and re.match(time_format, lines[7][len(prefix):].strip()):
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 8 should follow this format:\nTime Ended: 12:00 GMT+1",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 8 should follow this format:\nTime Ended: 12:00 GMT+1",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if len(lines) > 8:
            prefix = "Tablist Ended: "
            if lines[8].startswith(prefix) and re.match(r"^https://\S+$", lines[8][len(prefix):].strip()):
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 9 should follow the format:\nTablist Ended: https://tablist.org/xxx",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            embed = discord.Embed(
                title="Failed Submission",
                description="Line 9 should follow the format:\nTablist Ended: https://tablist.org/xxx",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if len(lines) > 10:
            if not lines[9].strip():
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Line 10 should be an empty line!",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            pass
        if len(lines) > 10:
            if lines[10].startswith("Notes: ") and len(lines[10][len("Notes: "):].strip()) > 0:
                pass
            else:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Invalid line in line 10. There may be nothing, or 'Notes: xxx' on line 10.",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return
        else:
            pass
        if len(lines) > 11:
            embed = discord.Embed(
                title="Failed Submission",
                description="You have too many lines made by 'Enter', please check the format",
                color=discord.Color.red()
            )
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("❌")
            return
        if True:
            start_str = lines[4].split("Time Started:")[1].strip().split()[0]
            end_str = lines[7].split("Time Ended:")[1].strip().split()[0]

            start_time = datetime.strptime(start_str, "%H:%M")
            end_time = datetime.strptime(end_str, "%H:%M")

            duration_minutes = (end_time - start_time).total_seconds() / 60
            if duration_minutes < 0:
                duration_minutes += 1440

            if duration_minutes < 30:
                embed = discord.Embed(
                    title="Failed Submission",
                    description="Your duty state must be at least 30 minutes long.",
                    color=discord.Color.red()
                )
                await message.reply(embed=embed, mention_author=True)
                await message.add_reaction("❌")
                return

            embed = discord.Embed(
                title="Successful Submission",
                description="You will receive a notification once an officer graded your duty state!",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            message_id = message.id
            user_id = message.author.id
            with sqlite3.connect("data/duty_states.db") as conn:
                c = conn.cursor()
                c.execute("INSERT INTO pending_duties (message_id, user_id) VALUES (?, ?)", (message_id, user_id))
                conn.commit()
            await message.reply(embed=embed, mention_author=True)
            await message.add_reaction("⚙️")
            return
    except Exception as e:
        print(f"Something went wrong listening to a duty state (message id = {message.id}: ", e)
        embed = discord.Embed(
            title="Something went wrong",
            description="Something went wrong checking your duty state's format. Please try again later.",
            color=discord.Color.yellow()
        )
        embed.set_footer(text="We are really sorry for this. You may contact <@926037474805948416> about the error.")
        await message.reply(embed=embed, mention_author=True)
        await message.add_reaction("❌")
        return
