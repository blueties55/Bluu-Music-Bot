import discord
from discord.ext import commands
import configparser
import logging
import asyncio

from settings import logger

def read_settings(file_path):
    config = configparser.ConfigParser()
    try:
        with open(file_path, encoding='utf-8') as f:
            config.read_file(f)
    except Exception as e:
        logger.error(f"Error reading the file: {e}")
        raise
    return config['DEFAULT']

def create_bot(settings):
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    intents.voice_states = True

    command_prefix = settings.get("command_prefix")
    mention_as_prefix = settings.get("mentions_as_prefix", "False").lower() == "true"

    if mention_as_prefix:
        return commands.Bot(command_prefix=commands.when_mentioned_or(command_prefix), intents=intents)
    else:
        return commands.Bot(command_prefix=command_prefix, intents=intents)

async def load_extensions(bot):
    extensions = ["cogs.player", "cogs.music_queue"]
    for ext in extensions:
        try:
            await bot.load_extension(ext)  # Await async load_extension
            logger.info(f"{ext} loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load {ext}: {e}")

async def main():
    settings = read_settings('settings.txt')
    DISCORD_API_TOKEN = settings.get("DISCORD_API_TOKEN", None)
    dm_response = settings.get("dm_response", None)

    if not DISCORD_API_TOKEN:
        logger.critical("DISCORD_API_TOKEN is missing in settings.txt")
        return

    bot = create_bot(settings)

    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        if isinstance(message.channel, discord.DMChannel):
            if dm_response:
                await message.add_reaction("👋")
                await message.author.send(dm_response)
            else:
                logger.warning("'dm_response' is empty in settings.txt. No response sent.")
        else:
            await bot.process_commands(message)

    await load_extensions(bot)  # Await async loading here

    await bot.start(DISCORD_API_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())