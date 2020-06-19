import os

import yaml
import discord
from typing import Any, Optional

with open(os.path.join(os.path.dirname(__file__), "../config.yml"), encoding="UTF-8") as f:
    _CONFIG_YAML = yaml.safe_load(f)


class _Config:
    def __init__(self, name: str, bot, guild: Optional[discord.guild] = None):
        self.name = name
        self.bot = bot
        self.guild = guild
        self._value = None

    async def get(self) -> Any:
        if self.guild is not None:
            if self.bot.db_conn is not None:
                ret = await self.bot.db_conn.fetchrow(
                    'SELECT $1 FROM guilds WHERE guild_id = $2',
                    self.name,
                    self.guild.id
                )
                self._value = ret
                return self._value
        else:
            print("DM")

    @property
    async def value(self):
        return self._value


class YAMLGetter(type):
    """
    ** STOLEN STRAIGHT FROM python-discord's BOT https://github.com/python-discord/bot **

    Implements a custom metaclass used for accessing
    configuration data by simply accessing class attributes.
    Supports getting configuration from up to two levels
    of nested configuration through `section` and `subsection`.
    `section` specifies the YAML configuration section (or "key")
    in which the configuration lives, and must be set.
    `subsection` is an optional attribute specifying the section
    within the section from which configuration should be loaded.
    Example Usage:
        # config.yml
        scott_bot:
            prefixes:
                direct_message: ''
                guild: '!'
        # config_cog.py
        class Prefixes(metaclass=YAMLGetter):
            section = "scott_bot"
            subsection = "prefixes"
        # Usage in Python code
        from config import Prefixes
        def get_prefix(scott_bot, message):
            if isinstance(message.channel, PrivateChannel):
                return Prefixes.direct_message
            return Prefixes.guild
    """

    subsection = None

    def __getattr__(cls, name):
        name = name.lower()

        try:
            if cls.subsection is not None:
                return _CONFIG_YAML[cls.section][cls.subsection][name]
            return _CONFIG_YAML[cls.section][name]
        except KeyError:
            dotted_path = '.'.join(
                (cls.section, cls.subsection, name)
                if cls.subsection is not None else (cls.section, name)
            )
            # log.critical(f"Tried accessing configuration variable at `{dotted_path}`, but it could not be found.")
            raise

    def __getitem__(cls, name):
        return cls.__getattr__(name)

    def __iter__(cls):
        """Return generator of key: value pairs of current constants class' config values."""
        for name in cls.__annotations__:
            yield name, getattr(cls, name)


class Bot(metaclass=YAMLGetter):
    section = "bot"

    default_prefix: str
    token: str
    color: int


class DataBase(metaclass=YAMLGetter):
    section = "database"

    db_url: str


class Emojis(metaclass=YAMLGetter):
    section = "messages"
    subsection = "emojis"

    first: str
    last: str
    left: str
    right: str

    delete: str


BOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
