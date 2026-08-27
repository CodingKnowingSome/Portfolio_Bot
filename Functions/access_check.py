"""
Functions used to check if a user can use a certain command.
"""
import discord
from Functions.cache_members import get_member
from functools import wraps


async def has_required_role(interaction: discord.Interaction, required_role_id: int) -> bool:
    """
    Checks if a user has the required role or a higher role.
    Args:
        interaction: The interaction object from discord.Interaction.
        required_role_id: The id of the required role.

    Returns: True/False.

    """
    required_role = interaction.guild.get_role(required_role_id)

    if not required_role:
        required_role = discord.utils.get(interaction.guild.roles, id=required_role_id)

    if not required_role:
        await interaction.response.send_message(f'Configuration error: Required role "{required_role_id}" not found.',
                                                ephemeral=True)
        return False

    has_permission = any(role.position >= required_role.position for role in interaction.user.roles)

    if not has_permission:
        await interaction.response.send_message(f'You must have at least {required_role.mention} role.', ephemeral=True)
        return False

    return True


def required_role(role_id: int):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            if not await has_required_role(interaction, role_id):
                return
            return await func(self, interaction, *args, **kwargs)

        return wrapper

    return decorator


async def has_required_role_member(guild: discord.Guild, user_id: int, required_role_id: int) -> bool:
    """
    Checks if a member has a given role.
    Args:
        guild: The server as discord.Guild.
        user_id: The id of the user to be checked.
        required_role_id: The id of the required role.

    Returns: True/False.

    """
    member = await get_member(guild, user_id)
    if member is None:
        return False
    return member.get_role(required_role_id) is not None
