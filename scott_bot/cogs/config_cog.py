from discord.ext import commands
from discord.ext.commands import Context
import discord

from scott_bot.converters import ConfigConverter

from scott_bot.bot import ScottBot
from scott_bot.util.config import DataBase, Defaults


INSERT_SQL = """
INSERT INTO $1 ({options})
    VALUES ({vals})
ON CONFLICT ON CONSTRAINT guilds_pkey
DO NOTHING;"""


class Config(commands.Cog):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.Cog.listener("on_guild_join")
    async def add_guild_db(self, guild: discord.Guild):
        if self.bot.db_conn is not None:
            defaults = {
                'guild_id': guild.id,
                'prefix': Defaults.prefix,
                'dad_name': Defaults.dad_name,
                'swearing': False
            }
            txt = INSERT_SQL.format(options=', '.join(defaults.keys()), vals=', '.join('$' + str(i) for i, x in enumerate(defaults.keys())))
            print(txt)
            x = await self.bot.db_conn.execute(
                txt,
                DataBase.main_tablename,
                *tuple(defaults.values())
                )
            print(x)

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
