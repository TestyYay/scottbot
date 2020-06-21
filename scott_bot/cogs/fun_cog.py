import random

from discord.ext import commands

from scott_bot.bot import ScottBot
from scott_bot.util.config import UwU


class FunCog(commands.Cog, name="Fun"):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.command(name="uwu", brief="Uwuify the provided text")
    async def _uwu(self, ctx: commands.Context, *text: str):
        """
        Uwuifies the provided text and adds a random lenny face to the end.

        Usage:
            {prefix}uwu <text>
        """
        text = " ".join(text)
        for key, value in UwU.replaces.items():
            text = text.replace(key, value)
        await ctx.send(text + ' ' + random.choice(UwU.faces))


def setup(bot: ScottBot):
    bot.add_cog(FunCog(bot))
