import asyncio

import discord
from discord.ext import commands


class StatusCog(commands.Cog, name="Status"):

    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.start_status_change())

    async def start_status_change(self):
        statuses = [
            "//help for commands",
            "//info for scott_bot info",
            "NEW //urbandictionary"
        ]
        while True:
            for status in statuses:
                await self.bot.change_presence(activity=discord.Game(name=status))
                await asyncio.sleep(10)


def setup(bot):
    bot.add_cog(StatusCog(bot))
