"""Implementation for @osintbuddybot (Discord)"""

import signal
import json
import sys
import os

from loguru import logger

import nextcord
from nextcord.ext import commands

from strings import TEMPLATES


def sigint_handler(sig, frame):
    """Handle SIGINT signal (e.g. Ctrl+C)"""
    logger.error("Got SIGINT, stopping...")

    sys.exit(0)


def setup(config_path: str) -> None:
    """Setup logging, get config, etc"""
    global logger, db_con, db_cur

    logger.remove(0)
    logger = logger.opt(colors=True)

    logger.add(sys.stderr, level="TRACE")

    with open(config_path, "r", encoding="UTF-8") as file:
        config = json.load(file)
        logger.debug("Loaded config from <m>{}</>", config_path)

    logs_path = config["logs_path"]
    if not os.path.exists(logs_path):
        logger.warning("Logs folder does not exist, creating... ({})",
                       logs_path)
        os.makedirs(logs_path)

    logger.add(os.path.join(
        logs_path, "log-{time}.log"), rotation="00:00", level="TRACE")

    logger.debug("Registering signal handler for <y>{}</>",
                 "signal.SIGINT")
    signal.signal(signal.SIGINT, sigint_handler)

    return config


def main(config_file: str = "config.json") -> None:
    """Start the bot"""
    global client, config
    logger.info("Starting the bot... (config_file=<m>{}</>)", config_file)

    config = setup(config_file)
    bot_token = config["discord"]["bot_token"]
    logger.debug("Retrieved Discord API tokens from config file")

    bot = commands.Bot()

    @bot.slash_command(description="Replies with pong!")
    async def ping(interaction: nextcord.Interaction):
        await interaction.send("Pong!", ephemeral=True)

    bot.run(bot_token)
    logger.error("Disconnected, stopping the script")


if __name__ == "__main__":
    logger.info('__name__ == "__main__", starting the program...')
    main()
