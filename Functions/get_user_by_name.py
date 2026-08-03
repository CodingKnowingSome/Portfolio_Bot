import discord


def find_member_by_name(guild: discord.Guild, target_name: str):
    target = target_name.strip().lower()

    for member in guild.members:
        if not member.nick:
            continue

        clean_nick = member.nick.split('|')[0].strip().lower()

        if clean_nick == target:
            return member

    return None