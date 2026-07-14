import discord

async def has_required_role(interaction: discord.Interaction, required_role_id: int) -> bool:
    required_role = interaction.guild.get_role(required_role_id)

    if not required_role:
        required_role = discord.utils.get(interaction.guild.roles, id=required_role_id)

    if not required_role:
        await interaction.response.send_message(f'Configuration error: Required role "{required_role_id}" not found.', ephemeral=True)
        return False

    has_permission = any(role.position >= required_role.position for role in interaction.guild.roles)

    if not has_permission:
        await interaction.response.send_message(f'You must have at least {required_role.mention} role.', ephemeral=True)
        return False

    return True