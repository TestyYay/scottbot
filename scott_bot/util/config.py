import os
from typing import Any, Optional

import discord
import yaml
from discord.ext import commands

with open(os.path.join(os.path.dirname(__file__), "../config.yml"), encoding="UTF-8") as f:
    _CONFIG_YAML = yaml.safe_load(f)


class _Config:
    def __init__(self, name: str, bot, guild: Optional[discord.Guild] = None):
        self.name = name
        self.bot = bot
        self.guild = guild
        self._value = None

    @staticmethod
    def _format_type(typ: str) -> Any:
        type_dict = {
            "bigint": int,
            "boolean": bool,
            "bool": bool,
            "anyarray": list,
            "varchar": str,
            "text": str,
            "integer": int,
            "character varying": str
        }
        return type_dict.get(typ)

    async def get_type(self):
        if self.bot.db_conn is not None:
            x = await self.bot.db_conn.fetchrow(
                "SELECT data_type FROM information_schema.columns WHERE table_name = $1 AND column_name = $2;",
                DataBase.main_tablename,
                self.name
            )
            return x.get("data_type")

    async def get(self) -> Any:
        if self.guild is not None:
            if self.bot.db_conn is not None:
                ret = await self.bot.db_conn.fetchrow(
                    f'SELECT {self.name} FROM {DataBase.main_tablename} WHERE guild_id = $1',
                    int(self.guild.id),
                )
                self._value = ret
                return self._value[self.name]
        else:
            return getattr(Defaults, self.name, None)

    async def set(self, new):
        if self.guild is not None:
            if self.bot.db_conn is not None:
                typ = await self.get_type()
                new = _Config._format_type(typ)(new)
                await self.bot.db_conn.execute(
                    f"""UPDATE {DataBase.main_tablename}
                            SET {self.name} = $1
                            WHERE guild_id = $2""",
                    new,
                    self.guild.id
                )


async def get_config(name: str, bot, guild: Optional[discord.Guild] = None) -> Optional[_Config]:
    if bot.db_conn is not None:
        cols = await bot.db_conn.fetch(
            "SELECT column_name FROM information_schema.columns WHERE table_name = $1;",
            DataBase.main_tablename
        )
        columns = [column.get("column_name") for column in cols]
        if name in columns:
            return _Config(name, bot, guild)


async def prefix_for(bot, message: discord.Message):
    config = await get_config("prefix", bot, message.guild)
    prefix = await config.get()
    return commands.when_mentioned_or(prefix)(bot, message)


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
    main_tablename: str
    nickname_tablename: str


class Defaults(metaclass=YAMLGetter):
    section = "database"
    subsection = "defaults"

    prefix: str
    dad_name: str
    swearing: bool


class Emojis(metaclass=YAMLGetter):
    section = "messages"
    subsection = "emojis"

    first: str
    last: str
    left: str
    right: str

    delete: str


class JoinMessages(metaclass=YAMLGetter):
    section = "messages"
    subsection = "join_messages"

    general: list
    swearing: list
    it_mems: list


BOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
