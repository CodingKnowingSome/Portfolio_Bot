"""
Handles IN removals by removing the role from the user.
"""
import discord
import config


async def in_remove_handler(client, message: discord.Message):
    """
    Removes the IN role from the user if the IN message is deleted.
    Args:
        client: The bot.
        message: The IN message as discord message.

    Returns: NA

    """
    guild = message.guild
    user = guild.get_member(message.author.id)
    if not user:
        try:
            user = await guild.fetch_member(message.author.id)
        except discord.NotFound:
            return
    has_in_role = user.get_role(config.IN_ROLE_ID) is not None
    if has_in_role:
        try:
            await user.remove_roles(discord.Object(id=config.IN_ROLE_ID))
            client.dispatch("leaderboard_update", "aa")
            client.dispatch("leaderboard_update", "officer")
        except discord.Forbidden:
            pass
    else:
        return
