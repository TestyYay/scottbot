from datetime import datetime

import discord
from discord.ext import commands

from ..bot import ScottBot
from ..util.constants import Logging, Bot


class LoggingCog(commands.Cog, name="Logging"):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self.bot.loop.create_task(self.on_ready())

    async def on_ready(self):
        await self.bot.wait_until_ready()
        if Logging.enabled:
            log_guild = self.bot.get_guild(Logging.guild_id)
            if log_guild is not None:
                channel = log_guild.get_channel(Logging.Channels.bot_start)
                if channel is not None:
                    embed = discord.Embed(title="Bot has started", color=Bot.color)
                    embed.set_footer(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f"))
                    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    await channel.send(embed=embed)

    @commands.Cog.listener("on_command_error")
    async def log_error(self, ctx: commands.Context, error):
        cog = ctx.cog
        if cog and cog._get_overridden_method(cog.cog_command_error) is None:
            ignored = (commands.CommandNotFound,)
            if isinstance(error, ignored):
                return
            if Logging.enabled:
                log_guild = self.bot.get_guild(Logging.guild_id)
                if log_guild is not None:
                    channel = log_guild.get_channel(Logging.Channels.errors)
                    if channel is not None:
                        embed = discord.Embed(title="Error", color=Bot.color)
                        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                        embed.description = f"""
__`Guild`__: {ctx.guild}
__`Channel`__: {ctx.channel}
__`Message`__: {ctx.message.content}
__`Error`__: **{error.__class__.__name__}**: {error}"""
                        await channel.send(embed=embed)
            else:
                raise error

    @commands.Cog.listener("on_guild_join")
    async def log_guild_join(self, guild: discord.Guild):
        if Logging.enabled:
            log_guild = self.bot.get_guild(Logging.guild_id)
            if log_guild is not None:
                channel = log_guild.get_channel(Logging.Channels.guild_join)
                if channel is not None:
                    embed = discord.Embed(title="Bot added", color=Bot.color)
                    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    embed.description = f"""
__`Guild`__: {guild}
__`Member Count`__: {guild.member_count}
__`Total Guild Count`__: {len(self.bot.guilds)}"""
                    await channel.send(embed=embed)

    @commands.Cog.listener("on_guild_remove")
    async def log_guild_leave(self, guild: discord.Guild):
        if Logging.enabled:
            log_guild = self.bot.get_guild(Logging.guild_id)
            if log_guild is not None:
                channel = log_guild.get_channel(Logging.Channels.guild_leave)
                if channel is not None:
                    embed = discord.Embed(title="Bot removed", color=Bot.color)
                    embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar_url)
                    embed.description = f"""
__`Guild`__: {guild}
__`Total Guild Count`__: {len(self.bot.guilds)}"""
                    await channel.send(embed=embed)


def setup(bot: ScottBot):
    bot.add_cog(LoggingCog(bot))
