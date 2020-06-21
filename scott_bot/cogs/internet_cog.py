import random
import re
from urllib.parse import urlencode

from discord.ext import commands

from scott_bot.bot import ScottBot


class InternetCog(commands.Cog, name="Internet"):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.command(name="youtube", brief="Search YouTube", aliases=("yt",))
    async def _yt_search(self, ctx: commands.Context, search_term: str):
        if self.bot.http_session is not None:
            query_string = urlencode({"search_query": search_term})
            async with self.bot.http_session.get("http://www.youtube.com/results?" + query_string) as r:
                if r.status == 200:
                    text = await r.text()
                    search_results = re.findall(r'href=\"/watch\?v=(.{11})', text)
                    vid_id = random.choice(search_results)
                    await ctx.send("http://www.youtube.com/watch?v=" + vid_id)


def setup(bot: ScottBot):
    bot.add_cog(InternetCog(bot))
