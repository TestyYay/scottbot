import re

from discord import Message
from discord.ext.commands import Cog

from ..bot import ScottBot
from ..util.config import get_config

DAD_MATCHER = re.compile(r"i('?)m (.+)", re.IGNORECASE)

BAD_MATCHER = re.compile(r"(i('?)m|i am) (.+) (and)?", re.IGNORECASE)


class DadCog(Cog, name="Dad"):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @Cog.listener("on_message")
    async def dad_message(self, message: Message):
        if message.author.id == self.bot.user.id:
            return
        match = DAD_MATCHER.match(message.content)
        if match:
            _dad_name = await get_config("dad_name", self.bot, message.guild)
            dad_name = await _dad_name.get()
            if dad_name:
                if BAD_MATCHER.match(match.group(2)):
                    await message.channel.send("lol u tried")
                else:
                    await message.channel.send('Hi, {}, I\'m {}'.format(match.group(2), dad_name))


def setup(bot: ScottBot):
    bot.add_cog(DadCog(bot))
