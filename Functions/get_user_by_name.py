"""
Finds the guild member object by the nick of the user.
#TODO: Make this better.
"""
import discord


def find_member_by_name(guild: discord.Guild, target_name: str):
    """
    Finds the guild member object by the nick of the user.
    Args:
        guild: The guild as discord.Guild.
        target_name: The name of the target to search for.

    Returns: The guild member object, or None if not found.

    """
    target = target_name.strip().lower()

    for member in guild.members:
        if not member.nick:
            continue

        clean_nick = member.nick.split('|')[0].strip().lower()

        if clean_nick == target:
            return member

    return None