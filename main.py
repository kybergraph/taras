"""Implementation for @osintbuddybot (Discord)"""

import signal
import json
import time
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
    greeting_channel_id = config["greeting_channel_id"]
    member_role_id = config["member_role_id"]
    sleep_time = config["sleep_time"]
    logger.debug("Retrieved neccessary data from config file")

    intents = nextcord.Intents.default()
    intents.members = True
    client = commands.Bot(intents=intents)

    @client.event
    async def on_member_join(member):
        """Respong to ping command"""
        # sender_name = member.nick
        logger.debug("Got on_member_join event, member.guild=<m>{}</>",
                     member.guild)

        # sleep so that welcome message doesn't come before join ack
        logger.trace("Waiting <m>{}</>s...", sleep_time)
        time.sleep(sleep_time)

        logger.debug("Sending welcome message to <m>{}</>", member)
        channel = client.get_channel(greeting_channel_id)
        await channel.send(TEMPLATES["welcome"].format(member.mention))

        logger.debug("Adding member role to <m>{}</>", member)
        member_role = member.guild.get_role(member_role_id)
        await member.add_roles(member_role)

    client.run(bot_token)
    logger.error("Disconnected, stopping the script")


if __name__ == "__main__":
    logger.info('__name__ == "__main__", starting the program...')
    main()
