"""
Returns the user id and name of a Roblox user by username using Roblox API.
"""
import requests
import logging

logger = logging.getLogger(__name__)


def get_roblox_id(username: str):
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
        username = username[0]
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
        logger.warning(f"Failed primary Roblox lookup for {clean_username}: {e}")

    try:
        search_url = f"https://users.roblox.com/v1/users/search?keyword={clean_username}&limit=10"
        search_resp = requests.get(search_url, timeout=5)
        if search_resp.status_code == 200:
            search_data = search_resp.json().get("data", [])
            for user in search_data:
                if user.get("name", "").lower() == clean_username.lower():
                    return user.get("id"), user.get("name")
    except Exception as e:
        logger.warning(f"Failed secondary Roblox lookup for {clean_username}: {e}")
    return None, None
