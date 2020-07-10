import glob
import os
import typing as t

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Context, Group

from ..bot import ScottBot
from ..converters import CommandConverter
from ..util import constants
from ..util.messages import get_cog_commands, get_group_commands, bad_arg_error
from ..util.pagination import HelpPaginator


def _get_code_lines() -> int:
    lines = 0
    py_files = glob.glob(os.path.join(constants.HOME_DIR, "**/*.py"), recursive=True)
    for file in py_files:
        try:
            with open(file) as f:
                lines += sum(1 for _ in f)
        except (FileNotFoundError, IOError):
            pass
    return lines


class HelpCog(Cog, name="Help"):

    def __init__(self, bot):
        self.bot: ScottBot = bot
        self._help.error(bad_arg_error)

    @commands.command(name="help", brief="Shows help for a command")
    async def _help(self, ctx: Context, command: CommandConverter = None):
        """
        Shows help for a command or a list of all commands.

        Usage:
            {prefix}help
            {prefix}help <command>

        Example:
            {prefix}help config
        """
        if command is None:
            other_commands = {}
            pages = []
            for cog in self.bot.cogs.values():
                if not getattr(cog, "hidden", False):
                    command_list = get_cog_commands(cog)
                    if cog.qualified_name != "Other":
                        if len(command_list) > 1:
                            self.add_page(cog.qualified_name, pages, command_list)
                        else:
                            other_commands.update(command_list)
                    else:
                        other_commands.update(command_list)
            no_cog = {comm.name: comm for comm in self.bot.commands if comm.cog is None and not comm.hidden}
            other_commands.update(no_cog)
            if other_commands:
                self.add_page("Other", pages, other_commands)

            embed = discord.Embed(title="Help Menu", color=constants.Bot.color)
            await HelpPaginator.paginate(
                ctx,
                embed,
                pages=pages,
                restrict_to_users=(ctx.author,)
            )
        else:
            help_format = """**```asciidoc
{comm}
{dashes}

{help}```**"""
            embed = discord.Embed(title="Help Menu", color=constants.Bot.color)
            comms = (
                dict({command.name: command}, **get_group_commands(command))
                if isinstance(command, Group)
                else {command.name: command}
            )
            pages = [
                help_format.format(comm=name, dashes='-' * len(name), help=comm.help.format(prefix=ctx.prefix))
                for name, comm in comms.items()
            ]
            await HelpPaginator.paginate(
                ctx,
                embed,
                pages=pages,
                restrict_to_users=(ctx.author,)
            )

    def add_page(self, name: str, pages: list, command_list: t.Dict[str, commands.Command]) -> None:
        help_page = f"""**```asciidoc
{name}
{'-' * len(name)}

{self._get_help_list(command_list)}```**"""
        pages.append(help_page)

    def _get_help_list(self, commands) -> str:
        if len(commands) <= 0:
            return "[There are no commands under this category]"
        i = max(len(x) for x in commands)
        s = ""
        for name, command in commands.items():
            s += f"{name:{i}} : {command.brief}\n"
        return s

    @commands.command(name="info", brief="Show info lol")
    async def _info(self, ctx: Context, guild: int = None, channel: int = None):
        """
        Show general information about the bot

        Usage:
        {prefix}info
        """
        invbot = 'https://discord.com/oauth2/authorize?client_id=613098957228212224&permissions=8&scope=bot'
        embed = discord.Embed(title="ScottBot", description="", color=constants.Bot.color)

        embed.add_field(name="Author", value="@ScottBot10#7361")
        embed.add_field(name="Servers with ScottBot", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="Lines of Code", value=str(_get_code_lines()))
        embed.add_field(name="Invite Link", value=f"[Add the bot]({invbot})")
        embed.add_field(name='Any Suggestions?', value='DM the bot: //suggest <suggestion>')

        msg = 'Info'
        if guild is not None and channel is not None:
            guild = self.bot.get_guild(guild)
            if guild:
                channel = guild.get_channel(channel)
                if channel is not None and channel in guild.channels:
                    await channel.send(msg, embed=embed)
        else:
            await ctx.send(msg, embed=embed)


def setup(bot: ScottBot):
    bot.add_cog(HelpCog(bot))
