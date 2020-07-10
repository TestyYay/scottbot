import os

import yaml
from dotenv import load_dotenv, find_dotenv

with open(os.path.join(os.path.dirname(__file__), "../config.yml"), encoding="UTF-8") as f:
    _CONFIG_YAML = yaml.safe_load(f)
load_dotenv(find_dotenv())


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


class Logging(metaclass=YAMLGetter):
    section = "logging"

    enabled: bool
    guild_id: int

    class Channels(metaclass=YAMLGetter):
        section = "logging"
        subsection = "channels"

        errors: int
        guild_join: int
        guild_leave: int


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


HOME_DIR = os.path.join(os.path.dirname(__file__), "../..")
BOT_DIR = os.path.abspath(HOME_DIR)
x = os.path.dirname(__file__)
