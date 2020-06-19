from discord.ext import commands
from discord.ext.commands import Context

from scott_bot.bot import Bot


class Config(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(name='config', aliases=('cfg',), invoke_without_command=True)
    async def config_group(self, ctx: Context):
        print("config")

    @config_group.command(name='help')
    async def config_help(self, ctx: Context):
        print("help")


def setup(bot: Bot):
    bot.add_cog(Config(bot))
