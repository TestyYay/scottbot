from discord.ext import commands

from scott_bot.bot import ScottBot


class SuggestionCog(commands.Cog, name="Suggestion"):
    def __init__(self, bot: ScottBot):
        self.bot = bot


def setup(bot: ScottBot):
    bot.add_cog(SuggestionCog(bot))
