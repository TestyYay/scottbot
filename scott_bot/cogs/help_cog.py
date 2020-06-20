import os

import discord
from discord.ext import commands
from discord.ext.commands import Cog, Context, BadArgument

from scott_bot.bot import ScottBot
from scott_bot.converters import CommandConverter
from scott_bot.util import config
from scott_bot.util.messages import wait_for_deletion, bad_arg_error
from scott_bot.util.pagination import HelpPaginator


def _get_code_lines():
    lines = 0
    py_files = []
    for root, dirs, files in os.walk(config.BOT_DIR):
        for file in files:
            if file.endswith(".py"):
                py_files.append(os.path.join(root, file))
    for file in py_files:
        try:
            with open(file) as f:
                lines += sum(1 for _ in f)
        except (FileNotFoundError, IOError):
            pass
    return lines


class Help(Cog):

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
            embed = discord.Embed(title="Help Menu", color=config.Bot.color)
            cogs = [
                cog for cog in self.bot.cogs.values()
                if not getattr(cog, "hidden", False)
                   and len(cog.get_commands()) > 0
            ]
            await HelpPaginator.paginate(
                ctx,
                embed,
                cogs,
                restrict_to_users=(ctx.author,)
            )
        else:
            embed = discord.Embed(title="Help Menu", color=config.Bot.color)
            embed.description = f"""**```asciidoc
{command.name}
{'-' * len(command.name)}

{command.help.format(prefix=ctx.prefix)}```**"""
            message = await ctx.send(embed=embed)
            await wait_for_deletion(message, (ctx.author,), client=self.bot)

    @commands.command(name="info", brief="Show info lol")
    async def _info(self, ctx: Context, guild: int = None, channel: int = None):
        """
        Show general information about the bot

        Usage:
        {prefix}info
        """
        invbot = 'https://bit.ly/3cuoNpo'
        embed = discord.Embed(title="ScottBot", description="", color=config.Bot.color)

        embed.add_field(name="Author", value="@ScottBot10#7361")
        embed.add_field(name="Servers with ScottBot", value=f"{len(self.bot.guilds)}")
        embed.add_field(name="Lines of Code", value=str(_get_code_lines()))
        embed.add_field(name="Invite Link", value=invbot)
        embed.add_field(name='Any Suggestions?', value='DM the bot: //suggest help')

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
    bot.add_cog(Help(bot))
