import os
from typing import Any, Optional, Sequence

import asyncpg
import discord
import yaml
from discord.ext import commands
from dotenv import load_dotenv, find_dotenv

with open(os.path.join(os.path.dirname(__file__), "../config.yml"), encoding="UTF-8") as f:
    _CONFIG_YAML = yaml.safe_load(f)
load_dotenv(find_dotenv())


class _Config:
    def __init__(self, name: str, bot, guild: Optional[discord.Guild] = None):
        self.name = name
        self.bot = bot
        self.guild = guild
        self.read_only = self.name in Config.bad

    @staticmethod
    def _format_type(typ: str, new) -> Any:
        def to_bool(x):
            lower = x.lower()
            return True if lower in ('yes', 'y', 'true', 't', '1', 'enable', 'on') else lower in (
                'no', 'n', 'false', 'f', '0', 'disable', 'off')

        type_dict = {
            "bigint": int,
            "boolean": to_bool,
            "bool": to_bool,
            "anyarray": list,
            "integer": int
        }
        typ = type_dict.get(typ)
        if typ:
            try:
                new = typ(new)
            except TypeError:
                new = None
        return new

    @staticmethod
    def to_channel(name, guild, x):
        if isinstance(x, int):
            if name in Config.channels:
                x = guild.get_channel(x)
        return x

    @staticmethod
    def from_channel(x):
        if isinstance(x, discord.TextChannel):
            x = x.id
        return x

    async def get_type(self):
        if self.bot.db_conn is not None:
            x = await self.bot.db_conn.fetchrow(
                "SELECT data_type, domain_name FROM information_schema.columns WHERE table_name = $1 AND column_name = $2;",
                DataBase.main_tablename,
                self.name
            )
            return x.get("domain_name") or x.get("data_type")

    async def get(self) -> Any:
        if self.guild is not None:
            if self.bot.db_conn is not None:
                ret = await self.bot.db_conn.fetchrow(
                    f'SELECT {self.name} FROM {DataBase.main_tablename} WHERE guild_id = $1',
                    int(self.guild.id),
                )
                return _Config.to_channel(self.name, self.guild, ret[self.name])
        else:
            return getattr(Defaults, self.name, None)

    @staticmethod
    async def get_multi(configs: Sequence[str], bot, guild: Optional[discord.Guild]) -> Optional[dict]:
        if guild is not None:
            if bot.db_conn is not None:
                ret = await bot.db_conn.fetchrow(
                    f'SELECT {", ".join(configs)} FROM {DataBase.main_tablename} WHERE guild_id = $1',
                    guild.id
                )
                return {key: _Config.to_channel(key, guild, val) for key, val in ret.items()}

    async def set(self, new):
        print("new")
        print(new)
        if self.read_only:
            raise AttributeError("The option is read-only")
        if self.guild is not None:
            if self.bot.db_conn is not None:
                typ = await self.get_type()
                new = _Config._format_type(typ, new)
                new = self.from_channel(new)
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


INSERT_SQL = """
INSERT INTO {table} ({options})
    VALUES ({vals})
ON CONFLICT ON CONSTRAINT guilds_pkey
DO NOTHING;"""


async def add_guild_db(db_conn: Optional[asyncpg.Connection], guild: discord.Guild):
    if db_conn is not None:
        defaults = {
            'guild_id': guild.id,
            'prefix': Defaults.prefix,
            'dad_name': Defaults.dad_name,
            'swearing': False
        }
        txt = INSERT_SQL.format(table=DataBase.main_tablename,
                                options=', '.join(defaults.keys()),
                                vals=', '.join('$' + str(i + 1) for i, x in enumerate(defaults.keys())))
        await db_conn.execute(
            txt,
            *tuple(defaults.values())
        )


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
        # admin_cog.py
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
    password: str
    main_tablename: str
    nickname_tablename: str
    suggestions_tablename: str


DataBase.db_url = os.getenv("DB_URL", DataBase.db_url)


class Config(metaclass=YAMLGetter):
    section = "config"

    bad: list
    channels: list

    class ConfigHelp(metaclass=YAMLGetter):
        section = "config"
        subsection = "help"

        prefix: str
        join_leave: str
        dad_name: str
        admin_channel: str
        swearing: str


class Defaults(metaclass=YAMLGetter):
    section = "config"
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


class IFTTT(metaclass=YAMLGetter):
    section = "ifttt"

    token: str
    suggestion: str


class UwU(metaclass=YAMLGetter):
    section = "messages"
    subsection = "uwu"

    faces: list
    replaces: dict


class Reddit(metaclass=YAMLGetter):
    section = "reddit"

    client_id: str
    client_secret: str
    user_agent: str
    username: str
    password: str


BOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
