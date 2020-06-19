from typing import Optional

from discord.ext.commands import Converter, Command, Context

from scott_bot.util.config import _Config, DataBase


class CommandConverter(Converter):

    async def convert(self, ctx: Context, command: str) -> Optional[Command]:
        commands = ctx.bot.all_commands
        if command in commands:
            return commands.get(command)


class ConfigConverter(Converter):

    async def convert(self, ctx: Context, option: str) -> Optional[_Config]:
        if ctx.bot.db_conn is not None:
            cols = await ctx.bot.db_conn.fetch(
                "SELECT column_name FROM information_schema.columns WHERE table_name = $1;",
                DataBase.main_tablename
            )
            columns = [column.get("column_name") for column in cols]
            if option in columns:
                return _Config(option, ctx.bot, ctx.guild)
