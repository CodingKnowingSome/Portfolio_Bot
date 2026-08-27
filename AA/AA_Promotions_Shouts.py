"""
When a log is accepted notifies the promoted personnel.
"""
import discord
import logging
import config
from AA.promotion_parser import parse_promotion_log

logger = logging.getLogger(__name__)


async def aa_promotions_shouts(message: discord.Message, client: discord.Client, guild: discord.Guild):
    """
    Sends a shout pinging the members in the server, includes all promoted personnel when a log is accepted.
    Args:
        message: The log message as a discord.Message.
        client: The bot.
        guild: The server as discord.Guild.

    Returns: NA

    """
    promotion_shouts_channel_id = config.PROMOTION_SHOUTS_CHANNEL_ID
    promotion_channel = client.get_channel(promotion_shouts_channel_id)

    try:
        names = parse_promotion_log(message.content)
    except ValueError as e:
        logger.error(f"Failed to parse AA log: {e}.")
        return
    stage = names.stage
    found_user = []
    names_list = []
    if not names.usernames:
        return
    for name in names.usernames:
        member = discord.utils.get(guild.members, display_name=name)

        if member:
            found_user.append(member.mention)
            names_list.append(name)
        else:
            names_list.append(name)

    passed = ", ".join(names_list)
    pings = ", ".join(found_user)

    promotion_messages = {
        1: {
            "title": "**You have been promoted to Cadet!**",
            "description": f"**{passed}, congratulations you have been promoted to Cadet! Head to https://discord.com/channels/804051193172197396/987692902278918234 and https://discord.com/channels/412291659347263498/987778002899312660 to receive your new roles.**"
        },
        2: {
            "title": "**You have been promoted to Junior Operative!**",
            "description": f"**{passed}, congratulations you have been promoted to Junior Operative! Head to https://discord.com/channels/804051193172197396/987692902278918234 and https://discord.com/channels/412291659347263498/987778002899312660 to receive your new roles.**"
        },
        3: {
            "title": "**You have been promoted to Operative!**",
            "description": f"**{passed}, congratulations on passing the AEGIS Academy, you have been promoted to Operative! Head to https://discord.com/channels/804051193172197396/987692902278918234 and https://discord.com/channels/412291659347263498/987778002899312660 to receive your new roles.**"
        }
    }
    promotion_message = promotion_messages.get(stage)
    if promotion_message is None:
        logger.warning(f"Unknown stage: {stage}.")
        return
    embed = discord.Embed(
        title=promotion_message["title"],
        description=promotion_message["description"].format(passed=passed),
        color=discord.Color.green()
    )
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1333019761554227251/1521160577244729394/image.png?ex=6a9049af&is=6a8ef82f&hm=90a11862d6f18cf058ad0d341dc59b1a8708a9db71fd4928ddcda73d039939ee&format=webp")
    await promotion_channel.send(content=pings, embed=embed)

    return
