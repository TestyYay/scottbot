import discord
from discord.ext import commands

from ..bot import ScottBot
from ..util.constants import Logging


class LoggingCog(commands.Cog, name="Logging"):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.Cog.listener("on_command_error")
    async def log_error(self, ctx: commands.Context, error):
        if Logging.enabled:
            log_guild = self.bot.get_guild(Logging.guild_id)
            if log_guild is not None:
                channel = log_guild.get_channel(Logging.Channels.errors)
                if channel is not None:
                    msg = f"""
__`Guild`__: {ctx.guild}
__`Channel`__: {ctx.channel}
__`Message`__: {ctx.message.content}
__`Error`__: **{error.__class__.__name__}**: {error}
"""
                    await channel.send(msg)

    @commands.Cog.listener("on_guild_join")
    async def log_guild_join(self, guild: discord.Guild):
        if Logging.enabled:
            log_guild = self.bot.get_guild(Logging.guild_id)
            if log_guild is not None:
                channel = log_guild.get_channel(Logging.Channels.guild_join)
                if channel is not None:
                    msg = f"""
__`Guild`__: {guild}
__`Member Count`__: {guild.member_count}
__`Total Guild Count`__: {len(self.bot.guilds)}
"""
                    await channel.send(msg)


def setup(bot: ScottBot):
    bot.add_cog(LoggingCog(bot))
