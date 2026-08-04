"""
Adds the IN role to a user, or removes it.
"""
import discord
import config


async def in_handler(message: discord.Message, guild: discord.Guild):
    """
    Adds the IN role to a user.
    Args:
        message: The IN message as discord.Message.
        guild: The guild as discord.Guild.

    Returns: NA

    """
    member = guild.get_member(message.author.id) or await guild.fetch_member(message.author.id)
    try:
        await member.add_roles(discord.Object(id=config.IN_ROLE_ID))
    except discord.Forbidden:
        return


async def in_deny_handler(message: discord.Message, guild: discord.Guild):
    """
    Removes the IN role from a user.
    Args:
        message: The IN message as discord.Message.
        guild: The guild as discord.Guild.

    Returns: NA

    """
    member = guild.get_member(message.author.id) or await guild.fetch_member(message.author.id)
    try:
        await member.remove_roles(discord.Object(id=config.IN_ROLE_ID))
    except discord.Forbidden:
        return