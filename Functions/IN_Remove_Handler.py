"""
Handles IN removals by removing the role from the user.
"""
import discord
from access_check import has_required_role_member
import config


async def in_remove_handler(message: discord.Message):
    """
    Removes the IN role from the user if the IN message is deleted.
    Args:
        message: The IN message as discord message.

    Returns: NA

    """
    valid1 = await has_required_role_member(message.guild, message.author.id, config.OFFICER_ROLE_ID)
    valid2 = await has_required_role_member(message.guild, message.author.id, config.OVERWATCH_ROLE_ID)
    if not valid1 and not valid2:
        guild = message.guild
        user = guild.get_member(message.author.id)
        if not user:
            user = guild.fetch_member(message.author.id)
        has_in_role = user.get_role(config.IN_ROLE_ID) is not None
        if has_in_role:
            try:
                await user.remove_roles(discord.Object(id=config.IN_ROLE_ID))
            except discord.Forbidden:
                pass
        else:
            return
