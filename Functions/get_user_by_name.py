"""
Finds the guild member object by the nick of the user.
#TODO: Make this better.
"""
import discord


def normal_user(user: str) -> str:
    return user.split("|", 1)[0].strip().casefold()


def find_member_by_name(guild: discord.Guild, target_name: str) -> discord.Member | None:
    """
    Finds the guild member object by the nick of the user.
    Args:
        guild: The guild as discord.Guild.
        target_name: The name of the target to search for.

    Returns: The guild member object, or None if not found.

    """
    target = normal_user(target_name)

    for member in guild.members:
        if not member.nick:
            continue

        if normal_user(member.nick) == target:
            return member

    return None
