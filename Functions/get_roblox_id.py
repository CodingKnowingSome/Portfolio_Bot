"""
Returns the user id and name of a Roblox user by username using Roblox API.
"""
import aiohttp
import logging
import requests

logger = logging.getLogger(__name__)


async def get_roblox_id(username: str) -> tuple[int | None, str | None]:
    """
    Returns the user id of a Roblox user by username using Roblox API.
    Args:
        username: The username of the Roblox user.

    Returns: The user's user id and name.

    """
    if not username:
        return None, None
    if "|" in username:
        username = username.split("|")[0]
    clean_username = username.strip()
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [clean_username], "excludeBannedUsers": False}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status != 200:
                    return None, None
                data = await response.json()
                users = data.get("data", [])
                if users:
                    user = users[0]
                    return user.get("id"), user.get("name")
    except aiohttp.ClientError as e:
        logger.warning(f"Roblox lookup failed for {clean_username}: {e}")
    return None, None


def get_roblox_id_sync(username: str) -> tuple[int | None, str | None]:
    """
    Returns the user id of a Roblox user by username using Roblox API.
    Args:
        username: The username of the Roblox user.

    Returns: The user's user id and name.

    """
    if not username:
        return None, None
    if "|" in username:
        username = username.split("|")[0]
    clean_username = username.strip()
    url = "https://users.roblox.com/v1/usernames/users"
    payload = {"usernames": [clean_username], "excludeBannedUsers": False}
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            res_json = response.json()
            data = res_json.get("data", [])
            if data:
                user_info = data[0]
                return user_info.get("id"), user_info.get("name")
    except Exception as e:
        logger.warning(f"Failed Roblox lookup for {clean_username}: {e}")
    return None, None
