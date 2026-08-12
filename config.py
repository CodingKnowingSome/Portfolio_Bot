"""
Configures variables based on the .env file.
"""
import os
import logging
from dotenv import load_dotenv
import secrets

load_dotenv()

logger = logging.getLogger(__name__)


class ConfigurationError(ValueError):
    """
    Configuration error.
    """
    pass


def get_env_int(key: str) -> int:
    """
    Get environment variable as integer.
    Args:
        key: The .env key.

    Returns: The environment variable value as integer.

    """
    value = os.getenv(key)
    if not value:
        raise ConfigurationError(f"Environment variable {key} not set.")
    try:
        return int(value)
    except ValueError:
        raise ConfigurationError(f'Environment variable "{key}" value {value} is not a valid integer.')


def get_env_str(key: str) -> str:
    """
    Get environment variable as string.
    Args:
        key: The .env key.

    Returns: The environment variable value as string.

    """
    value = os.getenv(key)
    if not value:
        raise ConfigurationError(f"Environment variable {key} not set.")
    try:
        return str(value)
    except ValueError:
        raise ConfigurationError(f'Environment variable "{key}" value {value} is not a valid string.')


try:
    #TOKEN
    DISCORD_TOKEN = get_env_str('DISCORD_TOKEN')

    #GUILD
    TEST_GUILD_ID = get_env_int('TEST_GUILD_ID')

    #channels
    LOG_CHANNEL_ID = get_env_int('LOG_CHANNEL_ID')
    AA_LOGS_CHANNEL_ID = get_env_int('AA_LOGS_CHANNEL_ID')
    ARCHIVE_CHANNEL_ID = get_env_int('ARCHIVE_CHANNEL_ID')
    DSGRADE_CHANNEL_ID = get_env_int('DSGRADE_CHANNEL_ID')
    DS_CHANNEL_ID = get_env_int('DS_CHANNEL_ID')
    LD_CHANNEL_ID = get_env_int('LD_CHANNEL_ID')
    PROMOTION_SHOUTS_CHANNEL_ID = get_env_int('PROMOTION_SHOUTS_CHANNEL_ID')
    AA_LD_CHANNEL_ID = get_env_int('AA_LEADERBOARD_CHANNEL_ID')
    AA_LD_ARCHIVE_ID = get_env_int('AA_LEADERBOARD_ARCHIVE_CHANNEL_ID')
    IN_CHANNEL_ID = get_env_int('IN_CHANNEL_ID')
    DATA_CHANNEL_ID = get_env_int('DATA_CHANNEL_ID')
    DATA_LOG_CHANNEL_ID = get_env_int('DATA_LOG_CHANNEL_ID')

    #roles
    PING_ROLE_ID = get_env_int('PING_ROLE_ID')
    GUEST_ROLE_ID = get_env_int('GUEST_ROLE_ID')
    OVERWATCH_ROLE_ID = get_env_int('OVERWATCH_ROLE_ID')
    ADMIN_ROLE_ID = get_env_int('ADMIN_ROLE_ID')
    OFFICER_ROLE_ID = get_env_int('OFFICER_ROLE_ID')
    IN_ROLE_ID = get_env_int('IN_ROLE_ID')
    TESTER_ROLE_ID = get_env_int('TESTER_ROLE_ID')

    #APIs
    API_URL = get_env_str('API_URL')
    API_KEY = secrets.token_hex(32)

    #Emoji names
    APPROVE_EMOJI_NAME = get_env_str('APPROVE_EMOJI_NAME')
    DENY_EMOJI_NAME = get_env_str('DENY_EMOJI_NAME')

    #Messages
    AA_MESSAGE_ID = get_env_int('AA_MESSAGE_ID')
    IN_MESSAGE_ID = get_env_int('IN_MESSAGE_ID')

except ConfigurationError as e:
    logger.critical(e)
    raise e
