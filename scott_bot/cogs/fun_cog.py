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

    @commands.command(name="trebuchet", brief="Trebuchet = good")
    async def _trebuchet(self, ctx: Context):
        msg = '''A trebuchet (French trébuchet) is a type of catapult that uses a swinging arm to throw a projectile. It was a common powerful siege engine until the advent of gunpowder.
    There are two main types of trebuchets.  The first is the traction trebuchet, or mangonel, which uses manpower to swing the arm. It first appeared in China in the 4th century BC. Carried westward by the Avars, the technology was adopted by the Byzantines in the late 6th century AD and by their neighbors in the following centuries.
    The later, and often larger, counterweight trebuchet, also known as the counterpoise trebuchet, uses a counterweight to swing the arm. It appeared in both Christian and Muslim lands around the Mediterranean in the 12th century, and made its way back to China via Mongol conquests in the 13th century.'''
        await ctx.send(msg)


def setup(bot: ScottBot):
    bot.add_cog(FunCog(bot))
