"""
Adds the IN role to a user, or removes it.
"""
import discord
import config


async def in_handler(client, message: discord.Message, guild: discord.Guild):
    """
    Adds the IN role to a user.
    Args:
        client: The bot.
        message: The IN message as discord.Message.
        guild: The guild as discord.Guild.

    Returns: NA

    """
    member = guild.get_member(message.author.id) or await guild.fetch_member(message.author.id)
    has_in_role = member.get_role(config.IN_ROLE_ID) is not None
    if not has_in_role:
        try:
            await member.add_roles(discord.Object(id=config.IN_ROLE_ID))
            client.dispatch("leaderboard_update", "aa")
            client.dispatch("leaderboard_update", "officer")
        except discord.Forbidden:
            return


async def in_deny_handler(client, message: discord.Message, guild: discord.Guild):
    """
    Removes the IN role from a user.
    Args:
        client: The bot.
        message: The IN message as discord.Message.
        guild: The guild as discord.Guild.

    Returns: NA

    """
    member = guild.get_member(message.author.id) or await guild.fetch_member(message.author.id)
    has_in_role = member.get_role(config.IN_ROLE_ID) is not None
    if has_in_role:
        try:
            await member.remove_roles(discord.Object(id=config.IN_ROLE_ID))
            client.dispatch("leaderboard_update", "aa")
            client.dispatch("leaderboard_update", "officer")
        except discord.Forbidden:
            return