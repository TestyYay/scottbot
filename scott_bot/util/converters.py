from typing import Optional

from discord.ext.commands import Converter, Command, Context, BadArgument

from scott_bot.util.config import _Config, get_config


class CommandConverter(Converter):

    async def convert(self, ctx: Context, command: str) -> Optional[Command]:
        commands = ctx.bot.all_commands
        if command in commands:
            return commands.get(command)
        raise BadArgument('Unknown command: "{}"'.format(command))


class ConfigConverter(Converter):

    async def convert(self, ctx: Context, option: str) -> Optional[_Config]:
        config = await get_config(option, ctx.bot, ctx.guild)
        if config is not None:
            return config
        raise BadArgument("Unknown config option: {}".format(option))
