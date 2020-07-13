from typing import Any, Optional, Sequence

import asyncpg
import discord
from discord.ext import commands

from scott_bot.util.constants import DataBase, Config, Defaults


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



