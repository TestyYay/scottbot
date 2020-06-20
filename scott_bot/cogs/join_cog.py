import random

import discord
from discord.ext.commands import Cog

from scott_bot.bot import ScottBot
from scott_bot.util.config import JoinMessages, get_config


class JoinMessage(Cog):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @Cog.listener("on_member_join")
    async def send_welcome_message(self, member: discord.Member):
        _join_leave = await get_config("join_leave", self.bot, member.guild)
        join_leave = await _join_leave.get()
        if join_leave:
            join_messages = JoinMessages.general
            _swearing = await get_config("swearing", self.bot, member.guild)
            swearing = await _swearing.get()
            if swearing:
                join_messages += JoinMessages.swearing
            if member.guild.id == 666932751060172800:
                join_messages += JoinMessages.it_mems
            channel = member.guild.get_channel(join_leave)
            if channel is not None:
                message = random.choice(join_messages).format(mention=member.mention)
                await channel.send(message)


def setup(bot: ScottBot):
    bot.add_cog(JoinMessage(bot))
