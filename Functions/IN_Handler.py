import discord
import config


async def in_handler(message: discord.Message, guild: discord.Guild):
    member = guild.get_member(message.author.id) or await guild.fetch_member(message.author.id)
    try:
        await member.add_roles(discord.Object(id=config.IN_ROLE_ID))
    except discord.Forbidden:
        return


async def in_deny_handler(message: discord.Message, guild: discord.Guild):
    member = guild.get_member(message.author.id) or await guild.fetch_member(message.author.id)
    try:
        await member.remove_roles(discord.Object(id=config.IN_ROLE_ID))
    except discord.Forbidden:
        return