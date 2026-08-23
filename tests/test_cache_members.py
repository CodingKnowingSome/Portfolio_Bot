from unittest.mock import Mock, AsyncMock, patch
import pytest
from Functions.cache_members import get_member
from Functions import cache_members
import discord


@pytest.fixture(autouse=True)
def clear_member_cache():
    cache_members.member_cache.clear()


@pytest.mark.asyncio
async def test_get_member_guild_cache():
    member = Mock()
    guild = Mock()
    guild.get_member.return_value = member
    guild.fetch_member = AsyncMock(return_value=member)
    result = await get_member(guild, 123)
    assert result == member
    guild.get_member.assert_called_once_with(123)
    guild.fetch_member.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_member_not_in_guild_cache():
    member = Mock()
    guild = Mock()
    guild.get_member.return_value = None
    guild.fetch_member = AsyncMock(return_value=member)
    result = await get_member(guild, 123)
    assert result == member
    guild.get_member.assert_called_once_with(123)
    guild.fetch_member.assert_called_once_with(123)


@pytest.mark.asyncio
async def test_get_member_using_cache_member():
    member = Mock()
    guild = Mock()
    guild.get_member.return_value = None
    guild.fetch_member = AsyncMock(return_value=member)
    first_result = await get_member(guild, 123)
    second_result = await get_member(guild, 123)
    assert first_result == member
    assert second_result == member
    guild.get_member.assert_any_call(123)
    guild.fetch_member.assert_awaited_once_with(123)


@pytest.mark.asyncio
async def test_get_member_cache_member_expire():
    first_member = Mock()
    second_member = Mock()
    guild = Mock()
    guild.id = 12345
    guild.get_member.return_value = None
    guild.fetch_member = AsyncMock(side_effect=[first_member, second_member])
    with patch("Functions.cache_members.time.monotonic", side_effect=[1000, 1061]):
        first_result = await get_member(guild, 456)
        second_result = await get_member(guild, 456)
    assert first_result == first_member
    assert second_result == second_member
    assert guild.fetch_member.await_count == 2


@pytest.mark.asyncio
async def test_get_member_cache_user_notfound():
    guild = Mock()
    guild.id = 12345
    guild.get_member.return_value = None
    guild.fetch_member = AsyncMock(side_effect=discord.NotFound(Mock(status=404), "Member Not Found"))
    result = await get_member(guild, 456)
    assert result is None
    guild.fetch_member.assert_awaited_once_with(456)