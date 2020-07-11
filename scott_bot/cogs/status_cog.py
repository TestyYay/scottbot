import asyncio

import discord
from discord.ext import commands

from ..bot import ScottBot


class StatusCog(commands.Cog, name="Status"):

    def __init__(self, bot: ScottBot):
        self.bot = bot
        self.bot.loop.create_task(self.start_status_change())

    async def start_status_change(self):
        await self.bot.wait_until_ready()
        statuses = [
            "//help for commands",
            "//info for scott_bot info",
            "NEW //urbandictionary"
        ]
        while True:
            for status in statuses:
                await self.bot.change_presence(activity=discord.Game(name=status))
                await asyncio.sleep(10)


def setup(bot: ScottBot):
    bot.add_cog(StatusCog(bot))
