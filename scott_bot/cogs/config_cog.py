import discord
from discord.ext import commands
from discord.ext.commands import Context

from scott_bot.bot import ScottBot
from scott_bot.converters import ConfigConverter
from scott_bot.util import config
from scott_bot.util.messages import bad_arg_error, wait_for_deletion

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
                'prefix': config.Defaults.prefix,
                'dad_name': config.Defaults.dad_name,
                'swearing': False
            }
            txt = INSERT_SQL.format(table=config.DataBase.main_tablename,
                                    options=', '.join(defaults.keys()),
                                    vals=', '.join('$' + str(i + 1) for i, x in enumerate(defaults.keys())))
            await self.bot.db_conn.execute(
                txt,
                *tuple(defaults.values())
            )

    @commands.group(name='config', aliases=('cfg',), brief="Change config for the server", invoke_without_command=True)
    async def _config_group(self, ctx: Context, config_option: ConfigConverter = None, new: str = None):
        """
        Change config for the server. You have to have Manage Server permissions to run this command.

        Usage:
            {prefix}config
            {prefix}config <option> <new>


        Example:
            {prefix}config dad_name "dad_bot"
        """
        if config_option is not None and new is not None:
            await config_option.set(new)
            await ctx.send(f"Changed config option {config_option.name} to {new}")
        else:
            cols = await self.bot.db_conn.fetch(
                "SELECT column_name FROM information_schema.columns WHERE table_name = $1;",
                config.DataBase.main_tablename
            )
            columns = [column.get("column_name") for column in cols if
                       column.get("column_name") not in config.Config.bad]
            embed = discord.Embed(title="Config Options")
            config_options = await self._get_config_options(columns, ctx.guild)
            embed.description = f"""**```{config_options}```**"""
            message = await ctx.send(embed=embed)
            await wait_for_deletion(message, (ctx.author,), client=self.bot)

    async def _get_config_options(self, options: list, guild):
        i = max(len(x) for x in options)
        s = ""
        values = await config._Config.get_multi(options, self.bot, guild)
        for key, value in values.items():
            s += f"{key:{i}} : {value}\n"
        return s

    # getattr(config.Config.ConfigHelp, option, 'None')
    # if option in config.Config.ConfigHelp.__annotations__:

    # @_config_group.error
    # async def _config_group_error(self, ctx: Context, error):
    #     if hasattr(error, "original"):
    #         if isinstance(error.original, AttributeError):
    #             await ctx.send("You can't change that option.")
    #     else:
    #         await bad_arg_error(None, ctx, error)

    @_config_group.command(name='help', brief="Shows help for a config option")
    async def _config_help(self, ctx: Context, config_option: ConfigConverter):
        """
        Shows help for a particular config option.

        Usage:
            {prefix}config help <option>

        Example:
            {prefix}config help dad_name
        """
        print(config.Config.ConfigHelp.__annotations__)
        print(config_option.name)
        if config_option.name in config.Config.ConfigHelp.__annotations__:
            embed = discord.Embed(title="Config Option")
            embed.description = f"""**```
{config_option.name}
{'-' * len(config_option.name)}
    
{getattr(config.Config.ConfigHelp, option, 'None')}
    ```**"""
            message = await ctx.send(embed=embed)
            await wait_for_deletion(message, (ctx.author,), client=self.bot)


def setup(bot: ScottBot):
    bot.add_cog(Config(bot))
