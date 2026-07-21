"""
Configures variables based on the .env file.
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class ConfigurationError(ValueError):
    """
    Configuration Error.
    """
    pass


def get_env_int(key: str) -> int:
    """
    Gets the content from the .env file in integer format.
    :param key: Ky for the .env.
    :return:
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
    Gets the content from the .env file in string format.
    :param key: Key for the .env.
    :return:
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
    AA_LOGS_CHANNEL_ID = get_env_int('AA_LOOG_CHANNEL_ID')
    ARCHIVE_CHANNEL_ID = get_env_int('ARCHIVE_CHANNEL_ID')
    DSGRADE_CHANNEL_ID = get_env_int('DSGRADE_CHANNEL_ID')
    DS_CHANNEL_ID = get_env_int('DS_CHANNEL_ID')
    LD_CHANNEL_ID = get_env_int('LD_CHANNEL_ID')
    PROMOTION_SHOUTS_CHANNEL_ID = get_env_int('PROMOTION_SHOUTS_CHANNEL_ID')

    #roles
    PING_ROLE_ID = get_env_int('PING_ROLE_ID')
    GUEST_ROLE_ID = get_env_int('GUEST_ROLE_ID')
    OVERWATCH_ROLE_ID = get_env_int('OVERWATCH_ROLE_ID')
    ADMIN_ROLE_ID = get_env_int('ADMIN_ROLE_ID')

except ConfigurationError as e:
    logger.critical(e)
    raise e
