"""
Functions used to check if a user can use a certain command.
"""
import discord


async def has_required_role(interaction: discord.Interaction, required_role_id: int) -> bool:
    """
    Cheks if a user has a given role a role above the given role.
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


async def has_required_role_member(guild: discord.Guild, user_id: int, required_role_id: int) -> bool:
    """
    Checks if a member has a given role.
    Args:
        guild: The server as discord.Guild.
        user_id: The id of the user to be checked.
        required_role_id: The id of the required role.

    Returns: True/False.

    """
    member = guild.get_member(user_id)
    if not member:
        member = await guild.fetch_member(user_id)
    has_role = member.get_role(required_role_id) is not None
    if has_role:
        return True
    else:
        return False
