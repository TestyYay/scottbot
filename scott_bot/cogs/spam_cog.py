from collections import defaultdict

import discord
from discord.ext import commands, tasks

from scott_bot.bot import ScottBot


class SpamCog(commands.Cog, name="Spam"):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self.loops = defaultdict(lambda: defaultdict(dict))

    async def send_message(self, channel: discord.TextChannel, message: str):
        async def _send():
            await channel.send(message)
        return _send

    @commands.group(name="spam", hidden=True, invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def _spam(self, ctx: commands.Context):
        if self.loops[ctx.guild.id][ctx.author]:
            print(self.loops)
            loop = self.loops[ctx.guild.id][ctx.author]
            if loop['count'] is None:
                await ctx.send(
                    f"You have a spammer running saying {loop['message']} every {loop['loop'].seconds} seconds. It has run {loop['loop'].current_loop} times.")
            else:
                await ctx.send(
                    f"You have a spammer running saying \"{loop['message']}\" {loop['loop'].count} times every {loop['loop'].seconds} seconds. It has run {loop['loop'].current_loop} times.")
        else:
            await ctx.send("You don't have any loops running on this server")

    @_spam.command(name="start", hidden=True)
    async def _start(self, ctx: commands.Context, *text: str, secs: int = 60, count=None):
        print(self.loops)
        if not self.loops[ctx.guild.id][ctx.author]:
            message = ' '.join(text)
            loop = tasks.Loop(self.send_message(ctx.channel, message), secs, 0, 0, count, True, None)
            self.loops[ctx.guild.id][ctx.author] = {"channel": ctx.channel, "message": message, "loop": loop}
            loop.start()
        else:
            await ctx.send(f"You already have a spammer running. Run `{ctx.prefix}spam stop` to stop it.")

    @_spam.command(name="stop", hidden=True)
    async def _stop(self, ctx: commands.Context):
        print(self.loops)
        if self.loops[ctx.guild.id][ctx.author]:
            self.loops[ctx.guild.id][ctx.author]["loop"].cancel()
            self.loops[ctx.guild.id].pop(ctx.author)
            await ctx.send(
                f"Spammer stopped at {self.loops[ctx.guild.id][ctx.author]['loop'].current_loop} iterations.")
        else:
            await ctx.send(f"You don't have a running spammer. Run `{ctx.prefix}spam start <message>` to start one.")

    @tasks.loop(seconds=10)
    async def git_url_spam(self):
        if self.channel is not None:
            await self.channel.send("https://github.com/ScottBot10/scottbot/invitations")


def setup(bot: ScottBot):
    bot.add_cog(SpamCog(bot))
