import os
import logging
from logging.config import dictConfig
import configparser

# Ensure the logs directory exists
LOG_DIR = "./logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Function to read settings from settings.txt
def read_settings(file_path):
    config = configparser.ConfigParser()
    config.read(file_path)
    
    settings = {}
    if 'DEFAULT' in config:
        for key, value in config['DEFAULT'].items():
            settings[key.strip()] = value.strip()
    return settings

# Read the settings from settings.txt
settings = read_settings('settings.txt')

# Fetch the necessary settings from settings.txt
DISCORD_API_TOKEN = settings.get("DISCORD_API_TOKEN")  # Ensure case matches
COMMAND_PREFIX = settings.get("command_prefix", "?")
DM_RESPONSE = settings.get("dm_response", "I am busy playing music.")
ALLOWED_CHANNEL_ID = settings.get("allowed_channel_id", "0")
LOG_FILE = settings.get("log_file", "bot.log")  # Fetch log file path

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "%(levelname)-10s - %(asctime)s - %(module)-15s : %(message)s"},
        "standard": {"format": "%(levelname)-10s - %(name)-15s : %(message)s"},
    },
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler", "formatter": "standard"},
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_DIR, LOG_FILE),  # Dynamic log file path
            "mode": "a",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "bot": {"handlers": ["console", "file"], "level": "INFO", "propagate": False},
        "discord": {"handlers": ["file"], "level": "INFO", "propagate": False},  # Ensure discord logs go to file
    },
}

# Apply logging configuration
dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("bot")
logger.info("Settings loaded successfully.")