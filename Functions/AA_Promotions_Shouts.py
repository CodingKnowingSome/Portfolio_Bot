"""
Sends a shout notifying the promoted students once the attendance log is approved.
"""
import discord
import logging
import config

logger = logging.getLogger('__name__')


async def aa_promotions_shouts(message: discord.Message, client: discord.Client, guild: discord.Guild):
    """
    Sends a shouts notifying the promoted students.
    :param message: The attendance log message.
    :param client: The bot.
    :param guild: The server.
    :return:
    """
    promotion_shouts_channel_id = config.PROMOTION_SHOUTS_CHANNEL_ID
    promotion_channel = client.get_channel(promotion_shouts_channel_id)

    lines = message.content.splitlines()
    stage_line = lines[3]
    start_stage = stage_line.index("Type:") + len("Type:")
    stage = stage_line[start_stage:].strip()
    line_9 = lines[9]
    start_index = line_9.index("username:") + len("username:")
    end_index = line_9.index("action:")

    names = line_9[start_index:end_index].strip()

    if names.strip():
        names_list = names.split(" ")
        found_user = []
        for name in names_list:
            member = discord.utils.get(guild.members, display_name=name)

            if member:
                found_user.append(member.mention)
            else:
                pass

        passed = ", ".join(names_list)
        pings = ", ".join(found_user)

        embed1 = discord.Embed(
            title="**You have been promoted to Cadet!**",
            description=f"**{passed}, congratulations you have been promoted to Cadet! Head to https://discord.com/channels/804051193172197396/987692902278918234 and https://discord.com/channels/412291659347263498/987778002899312660 to receive your new roles.**",
            color=discord.Color.green()
        )

        embed2 = discord.Embed(
            title="**You have been promoted to Junior Operative!**",
            description=f"**{passed}, congratulations you have been promoted to Junior Operative! Head to https://discord.com/channels/804051193172197396/987692902278918234 and https://discord.com/channels/412291659347263498/987778002899312660 to receive your new roles.**",
            color=discord.Color.green()
        )

        embed3 = discord.Embed(
            title="**You have been promoted to Operative!**",
            description=f"**{passed}, congratulations on passing the AEGIS Academy, you have been promoted to Operative! Head to https://discord.com/channels/804051193172197396/987692902278918234 and https://discord.com/channels/412291659347263498/987778002899312660 to receive your new roles.**",
            color=discord.Color.green()
        )

        if stage == "1":
            await promotion_channel.send(content=pings, embed=embed1)

        if stage == "2":
            await promotion_channel.send(content=pings, embed=embed2)

        if stage == "3":
            await promotion_channel.send(content=pings, embed=embed3)



    else:
        return
