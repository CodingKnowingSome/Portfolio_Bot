"""
Checks if the message sent in the duty state channel follows the correct format.
"""
import discord
from datetime import datetime
import re
import aiosqlite
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DutyStateValidation:
    valid: bool
    correct: str


async def duty_state_validation(content: str) -> DutyStateValidation:
    lines = content.splitlines()
    correct = ""
    errors = []
    if len(lines) < 1 or not lines[0].startswith("Username: "):
        correct += lines[0] + "<- Should be: 'Username: [username]'\n"
        errors.append(1)
    else:
        correct += lines[0] + '\n'
    if len(lines) < 2 or not lines[1].startswith("Duty: "):
        correct += lines[1] + "<- Should be: 'Duty: [your duty]'\n"
        errors.append(2)
    else:
        correct += lines[1] + '\n'
    if len(lines) < 3 or not re.match(
            "^https?:\/\/(?:www\.)?(?:prnt\.sc|prntscr\.com|gyazo\.com|i\.gyazo\.com|imgur\.com|i\.imgur\.com)\/.*$",
            lines[2]):
        correct += lines[2] + "<- Should be a link to your duty proof from Lightshot/Gyazo/imgur\n"
        errors.append(3)
    else:
        correct += lines[2] + '\n'
    if len(lines) < 4 or not lines[3] == "":
        correct += lines[3] + "<- Line 4 should be empty\n"
        errors.append(4)
    else:
        correct += lines[3] + '\n'
    if len(lines) < 5 or not lines[4].startswith("Time Started: "):
        correct += lines[4] + "<- Should be: 'Time Started: xx:yy GMT+-zz'\n"
        errors.append(5)
    elif not re.match("^(?:[01][0-9]|2[0-3]):[0-5][0-9]\s?GMT[+-](?:1[0-4]|0?[0-9])$",
                      lines[4][len("Time Started: "):]):
        correct += lines[4] + "<- The time must be in xx:yy GMT+-zz format\n"
        errors.append(5)
    else:
        correct += lines[4] + '\n'
    if len(lines) < 6 or not lines[5].startswith("Tablist Started: "):
        correct += lines[5] + "<- Should be: 'Tablist Started: [link]'"
        errors.append(6)
    elif not re.match(
            "^https?:\/\/(?:www\.)?(?:prnt\.sc|prntscr\.com|gyazo\.com|i\.gyazo\.com|imgur\.com|i\.imgur\.com)\/.*$",
            lines[5][len("Tablist Started: "):]):
        correct += lines[5] + '<- The link must be from: Lightshot/Gyazo/imgur\n'
        errors.append(6)
    else:
        correct += lines[5] + '\n'
    if len(lines) < 7 or not lines[6] == "":
        correct += lines[6] + "<- Should be empty\n"
        errors.append(7)
    else:
        correct += lines[6] + '\n'
    if len(lines) < 8 or not lines[7].startswith("Time Ended: "):
        correct += lines[7] + "<- Should be: 'Time Ended: xx:yy GMT+-zz'\n"
        errors.append(8)
    elif not re.match("^(?:[01][0-9]|2[0-3]):[0-5][0-9]\s?GMT[+-](?:1[0-4]|0?[0-9])$",
                      lines[7][len("Time Ended: "):]):
        correct += lines[7] + "<- The time must be in xx:yy GMT+-zz format\n"
        errors.append(8)
    else:
        correct += lines[7] + '\n'
    if len(lines) < 9 or not lines[8].startswith("Tablist Ended: "):
        correct += lines[8] + "<- Should be: 'Tablist Ended: [link]'"
        errors.append(9)
    elif not re.match(
            "^https?:\/\/(?:www\.)?(?:prnt\.sc|prntscr\.com|gyazo\.com|i\.gyazo\.com|imgur\.com|i\.imgur\.com)\/.*$",
            lines[8][len("Tablist Ended: "):]):
        correct += lines[8] + '<- The link must be from: Lightshot/Gyazo/imgur\n'
        errors.append(9)
    else:
        correct += lines[8] + '\n'
    if len(lines) >= 10:
        if not lines[9] == "":
            correct += lines[9] + "<- Should be empty\n"
            errors.append(10)
        else:
            correct += lines[9] + '\n'
    if len(lines) == 11:
        if not lines[10].startswith("Notes: "):
            correct += lines[10] + "<- Should be 'Notes: [note]'"
            errors.append(11)
        else:
            correct += lines[10]
    return DutyStateValidation(
        valid=not errors,
        correct=correct
    )


async def dutylistener(message: discord.Message):
    validated = await duty_state_validation(message.content)
    status = validated.valid
    if status:
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
            color=discord.Color.green(),
            title="Submission Succeeded!",
            timestamp=datetime.now(),
            description="Your duty state is now in the processing queue. You'll be notified when your duty state has been graded by one of our officers!"
        )
        embed.add_field(name="Length of duty state:", value=f"{hours}h {minutes}m")
        embed.set_footer(text="CodingKnowingSome")
        await message.reply(embed=embed)
        async with aiosqlite.connect("data/duty_states.db") as conn:
            await conn.execute("""
            INSERT INTO pending_duties VALUES (?, ?)
            """, (message.id, message.author.id))
            await conn.commit()
        await message.add_reaction("⚙️")
    else:
        embed = discord.Embed(
            title="Submission Failed!",
            description="It seems that there's an issue with your duty state!\nSee above on how you can correct it, then you can repost it.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        embed.set_footer(text="CodingKnowingSome")
        await message.reply(f"```{validated.correct}```", embed=embed)
        await message.add_reaction("❌")
