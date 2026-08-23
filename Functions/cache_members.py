import discord
import time

cache_time = 60

member_cache: dict[
    tuple[int, int],
    tuple[discord.Member, float]
] = {}


async def get_member(guild: discord.Guild, user_id: int) -> discord.Member | None:
    member = guild.get_member(user_id)
    if member is not None:
        return member
    key = (guild.id, user_id)
    now = time.monotonic()
    cached = member_cache.get(key)
    if cached is not None:
        member, cached_at = cached
        if now - cached_at < cache_time:
            return member
        del member_cache[key]
    try:
        member = await guild.fetch_member(user_id)
    except discord.NotFound:
        return None
    member_cache[key] = (member, now)
    return member
