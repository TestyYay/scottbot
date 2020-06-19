from discord.ext.commands import BadArgument, Converter, Command, Context
from scott_bot.bot import Bot
from typing import Union, List


class CommandConverter(Converter):

    async def convert(self, ctx: Context, command: str) -> Union[Command, List[Command]]:
        commands = ctx.bot.all_commands
        if command in commands:
            return commands.get(command)
        return list(commands.values())
