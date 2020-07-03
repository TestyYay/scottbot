from discord.ext import commands

from ..bot import ScottBot


# from apraw.models.helpers.listing_generator import ListingGenerator


class RedditCog(commands.Cog, name="reddit"):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.group(name="reddit", invoke_without_command=True)
    async def _reddit(self, ctx: commands.Context):
        if self.bot.reddit is not None:
            _random_sub = await self.bot.reddit.subreddit("random")
            random_post = ListingGenerator(self.bot.reddit, f"/r/{_random_sub.display_name}/random",
                                           subreddit=_random_sub)

            async for submission in random_post.get():
                print(submission)


def setup(bot: ScottBot):
    pass
    # bot.add_cog(RedditCog(bot))
