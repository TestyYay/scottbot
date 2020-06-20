import discord
from discord.ext import commands
from discord.ext.commands import Context

from scott_bot.bot import ScottBot
from scott_bot.converters import ConfigConverter
from scott_bot.util.config import DataBase, Defaults
from scott_bot.util.messages import bad_arg_error

INSERT_SQL = """
INSERT INTO {table} ({options})
    VALUES ({vals})
ON CONFLICT ON CONSTRAINT guilds_pkey
DO NOTHING;"""


class Config(commands.Cog):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        # self._config_group.error(bad_arg_error)
        self._config_help.error(bad_arg_error)

    @commands.Cog.listener("on_guild_join")
    async def add_guild_db(self, guild: discord.Guild):
        if self.bot.db_conn is not None:
            defaults = {
                'guild_id': guild.id,
                'prefix': Defaults.prefix,
                'dad_name': Defaults.dad_name,
                'swearing': False
            }
            txt = INSERT_SQL.format(table=DataBase.main_tablename,
                                    options=', '.join(defaults.keys()),
                                    vals=', '.join('$' + str(i + 1) for i, x in enumerate(defaults.keys())))
            await self.bot.db_conn.execute(
                txt,
                *tuple(defaults.values())
            )

    @commands.group(name='config', aliases=('cfg',), brief="Change config for the server", invoke_without_command=True)
    async def _config_group(self, ctx: Context, config_option: ConfigConverter, new: str):
        """
        Change config for the server. You have to have Manage Server permissions to run this command.

        Usage:
            {prefix}config
            {prefix}config <option> <new>


        Example:
            {prefix}config dad_name "dad_bot"
        """
        await config_option.set(new)
        await ctx.send(f"Changed config option {config_option.name} to {new}")

    @_config_group.error
    async def _config_group_error(self, ctx: Context, error):
        if isinstance(getattr(error, "orininal", Exception), AttributeError):
            await ctx.send("You can't change that option.")
        else:
            await bad_arg_error(None, ctx, error)

    @_config_group.command(name='help', brief="Shows help for a config option")
    async def _config_help(self, ctx: Context, config_option: ConfigConverter):
        """
        Shows help for a particular config option.

        Usage:
            {prefix}config help <option>

        Example:
            {prefix}config help dad_name
        """
        x = await config_option.get()
        await ctx.send(str(x))


def setup(bot: ScottBot):
    bot.add_cog(Config(bot))
