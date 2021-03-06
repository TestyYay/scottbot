from collections import defaultdict

import discord
from discord.ext import commands, tasks

from ..bot import ScottBot


class SpamCog(commands.Cog, name="Spam"):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self.loops = defaultdict(lambda: defaultdict(dict))

    def send_message(self, channel: discord.TextChannel, message: str):
        async def _send():
            await channel.send(message)

        return _send

    @commands.group(name="spam", hidden=True, invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def _spam(self, ctx: commands.Context):
        if self.loops[ctx.guild.id][ctx.author]:
            loop = self.loops[ctx.guild.id][ctx.author]
            if loop['loop'].count is None:
                await ctx.send(
                    f"You have a spammer running saying {loop['message']} every {loop['loop'].seconds} seconds. It has run {loop['loop'].current_loop} times.")
            else:
                await ctx.send(
                    f"You have a spammer running saying \"{loop['message']}\" every {loop['loop'].seconds} seconds {loop['loop'].count} times. It has run {loop['loop'].current_loop} times.")
        else:
            await ctx.send("You don't have any loops running on this server")

    @_spam.command(name="start", hidden=True)
    async def _start(self, ctx: commands.Context, text: str, secs: int = 60, count: int = None):
        if not self.loops[ctx.guild.id][ctx.author]:
            func = self.send_message(ctx.channel, text)
            loop = tasks.Loop(func, secs, 0, 0, count, True, None)
            self.loops[ctx.guild.id][ctx.author] = {"channel": ctx.channel, "message": text, "loop": loop}
            loop.start()
            await ctx.send("Spammer started!")
        else:
            await ctx.send(f"You already have a spammer running. Run `{ctx.prefix}spam stop` to stop it.")

    @_spam.command(name="stop", hidden=True)
    async def _stop(self, ctx: commands.Context):
        if self.loops[ctx.guild.id][ctx.author]:
            self.loops[ctx.guild.id][ctx.author]["loop"].cancel()
            await ctx.send(
                f"Spammer stopped at {self.loops[ctx.guild.id][ctx.author]['loop'].current_loop} iterations.")
            self.loops[ctx.guild.id].pop(ctx.author)
        else:
            await ctx.send(f"You don't have a running spammer. Run `{ctx.prefix}spam start <message>` to start one.")

    @tasks.loop(seconds=10)
    async def git_url_spam(self):
        if self.channel is not None:
            await self.channel.send("https://github.com/ScottBot10/scottbot/invitations")


def setup(bot: ScottBot):
    bot.add_cog(SpamCog(bot))
