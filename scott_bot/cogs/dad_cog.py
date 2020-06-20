import re

from discord import Message
from discord.ext.commands import Cog

from scott_bot.bot import ScottBot
from scott_bot.util.config import get_config

DAD_PATTERN = r"i('?)m (.+)"
DAD_MATCHER = re.compile(dad_pattern, re.IGNORECASE)

BAD_PATTERN = r"(i('?)m|i am) (.+) (and)?"
BAD_MATCHER = re.compile(bad_pattern, re.IGNORECASE)


class DadCog(Cog):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @Cog.listener("on_message")
    async def dad_message(self, message: Message):
        if message.author.id == bot.user.id:
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
