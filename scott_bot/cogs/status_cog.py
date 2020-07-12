from itertools import cycle

import discord
from discord.ext import commands
from discord.ext import tasks

from ..bot import ScottBot


class StatusCog(commands.Cog, name="Status"):

    def __init__(self, bot: ScottBot):
        self.bot = bot
        self.statuses = cycle([
            "//help for commands",
            "//info to get info",
            "NEW //giveaway",
            "//help giveaway",
            "//config to change config"
        ])
        self.start_status_change.start()

    @tasks.loop(seconds=10)
    async def start_status_change(self):
        await self.bot.change_presence(activity=discord.Game(name=next(self.statuses)))


def setup(bot: ScottBot):
    bot.add_cog(StatusCog(bot))
