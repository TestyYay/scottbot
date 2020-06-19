from discord.ext import commands
from discord.ext.commands import Context

from scott_bot.converters import ConfigConverter

from scott_bot.bot import ScottBot


class Config(commands.Cog):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.group(name='config', aliases=('cfg',), invoke_without_command=True)
    async def config_group(self, ctx: Context, option: str, new: str):
        print("config")
        print(option, new)

    @config_group.command(name='help')
    async def config_help(self, ctx: Context, config_option: ConfigConverter):
        print(config_option)
        print("help")


def setup(bot: ScottBot):
    bot.add_cog(Config(bot))
