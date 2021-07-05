import datetime
import logging
import time
from discord.utils import get
from logging.handlers import RotatingFileHandler

import discord
from discord.ext import commands

import util.gen_list as GenList
from util.config import BotConfig
from util.data.data_backup import backup_databases
from util.data.guild_data import GuildData
from util.features import get_extensions, get_commands_blacklist
from util.help_command import HelpCommand
from util.logging import ConsoleColorFormatter


log = logging.getLogger("discordbot")

start_time = time.time()

class DiscordBot(commands.Bot):
    """
    Default Bot Class that handles the initial bot creation
    """

    def __init__(self):
        
        self.load_config()

        try:
            self.setup_logging()
        except Exception as e:
            log.error(f"Logging config error!\n{e}")
            raise Exception(f"Logging config error!\n{e}")

        self.logger = log

        log.info("Starting bot...")

        intents = discord.Intents(
            guilds = True,
            members = True,
            messages = True,
            reactions = True,
            presences = True
        )

        super().__init__(command_prefix=self.prefix, help_command=HelpCommand(), intents=intents)

        self.extns = get_extensions()

    def load_config(self):
        """
        Loads the bot config file, filling in values.
        """

        self.bot_token = None
        self.load_music = None
        try:
            log.info("Loading config...")
            self.config = BotConfig()
            self.config_data = self.config.data
            self.bot_data = self.config_data["bot"]
            self.bot_token = self.bot_data["token"]
            self.bot_key = self.bot_data["key"]
            self.bot_owners = self.bot_data["owners"]
            self.create_commands_list = self.config_data["misc"]["create_commands_list"]
            self.logging_data = self.config_data["logging"]

            self.do_run = self.config.do_run
        except KeyError as e:
            log.fatal(f"Config error.\n\tKey Not Loaded: {e}")
            self.do_run = False

    def setup_logging(self):
        """
        Sets up the logging configuration for the bot.
        """

        log_file = self.logging_data["file"]
        log_console = self.logging_data["console"]

        logging.getLogger("discord").setLevel(logging.INFO)
        logging.getLogger("discord.http").setLevel(logging.WARNING)
        # logging.getLogger("discord.state").setLevel(logging.INFO)

        current_time = datetime.datetime.now()
        filename = f'{log_file["file_location"]}/{current_time.strftime("%m%y")}.log'

        log.setLevel(self.get_log_level(log_file["level"]))

        max_bytes = log_file["max_mebibytes"] * 1024 * 1024 # Bytes -> MiB conversion
        handler = RotatingFileHandler(filename=filename, encoding=log_file["encoding"], 
            mode=log_file["write_mode"], backupCount=log_file["backup_count"], maxBytes=max_bytes)
        fmt = logging.Formatter(log_file["format"], log_file["date_time_format"], style=log_file["style"])
        handler.setFormatter(fmt)
        log.addHandler(handler)

        console = logging.StreamHandler()
        console_fmt = ConsoleColorFormatter(log_console["format"], log_console["date_time_format"], style=log_console["style"], colored=log_console["colored"])
        console.setFormatter(console_fmt)
        console.setLevel(self.get_log_level(log_console["level"]))
        log.addHandler(console)
    
        log.info("- - - - - - - - - - - - - - - - - - ")
        log.info(f"Logging initialized. Logging to console and `{filename}`.")

    def get_log_level(self, name: str):
        """Get the log level from a given name

        Args:
            name (str): Log level

        Returns:
            constant: Log level constant from the logging module
        """

        valid = ["debug", "info", "warning", "error", "critical"]
        log_cfg = name

        if log_cfg.lower() in valid:
            return getattr(logging, log_cfg.upper())

        return logging.INFO

    def prefix(self, bot, message):
        """Get the bot prefix based on the config and guild settings.

        Args:
            bot (discord.Bot): The Discord bot
            message (discord.Message): Message in which the command was used

        Returns:
            str: The bot prefix
        """

        pfx = self.bot_key
        if message.guild:
            data = GuildData(str(message.guild.id)).strings.fetch_by_name("prefix")
            if data:
                pfx = commands.when_mentioned_or(data)(bot, message)
            else: 
                pfx = commands.when_mentioned_or(self.bot_key)(bot, message)
        return pfx if pfx else self.bot_key

    def load_extensions(self):
        """Load extensions from the config file
        """

        if not self.do_run:
            return

        count = 0
        for extension in self.extns:
            try:
                self.load_extension(extension)
                log.info(f"Cog Loaded | {extension}")
                count += 1
            except Exception as error:
                log.error(f"{extension} cannot be loaded. \n\t[{error}]")
        log.info(f"Loaded {count}/{len(self.extns)} cogs")

    def unload_commands(self):
        """Unload commands as specified in the config file.
        """

        bl_cmds = get_commands_blacklist()

        if len(bl_cmds) == 0:
            log.debug("No commands to blacklist")
            return
        
        count = 0
        for cmd in bl_cmds:
            self.remove_command(cmd)
            log.info(f"Removed {cmd}")
            count += 1

        log.info(f"Removed {count}/{len(bl_cmds)} commands")

    def run(self):
        """Run the bot.
        """

        if self.do_run:
            super().run(self.bot_token)
        else:
            log.fatal("Startup aborted.")

    def generate_commands_lists(self):
        """Generate a list of commands, their aliases, and descriptions
        """

        if self.create_commands_list:
            generator = GenList.Generator(bot)
            generator.gen_md_list()


log.info("Starting...")

bot = DiscordBot()

@bot.event
async def on_ready():
    """
    Called when the bot is ready.
    """

    log.info(f"We have logged in as {bot.user}")
    
    await bot.change_presence(activity=discord.Activity(
        name=f"Do {bot.bot_key}help", type=discord.ActivityType.playing))

    backup_databases()

    bot.generate_commands_lists()

    log.info("Bot started in {} seconds".format(str(time.time() - start_time)[:4]))

@bot.event
async def on_message(message):
    """Called when a message is sent
    """

    if message.author == bot.user:
        return

    await bot.process_commands(message)

if __name__ == "__main__":
    bot.load_extensions()
    bot.unload_commands()

bot.run()
