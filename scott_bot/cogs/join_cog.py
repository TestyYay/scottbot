import random

import discord
from discord.ext.commands import Cog

from ..bot import ScottBot
from ..util.config import get_config
from ..util.constants import JoinMessages
from ..util.messages import ifttt_notify


class JoinMessageCog(Cog, name="JoinMessage"):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @Cog.listener("on_guild_join")
    async def on_guild_join(self, guild: discord.Guild):
        print("Bot added to server: " + guild.name)
        await ifttt_notify(self.bot.http_session, (str(self.bot.user.name), guild.name,
                                                   f"There are {len(self.bot.guilds)} servers with {self.bot.user.name} on them. {guild.name} has {guild.member_count} members"),
                           name="bot_join_server")

    @Cog.listener("on_member_join")
    async def send_welcome_message(self, member: discord.Member):
        _join_leave = await get_config("join_leave", self.bot, member.guild)
        join_leave = await _join_leave.get()
        if join_leave is not None:
            join_messages = JoinMessages.general
            _swearing = await get_config("swearing", self.bot, member.guild)
            swearing = await _swearing.get()
            if swearing:
                join_messages += JoinMessages.swearing
            if member.guild.id == 666932751060172800:
                join_messages += JoinMessages.it_mems
            message = random.choice(join_messages).format(mention=member.mention)
            await join_leave.send(message)


def setup(bot: ScottBot):
    bot.add_cog(JoinMessageCog(bot))
