import random
import re
from urllib.parse import urlencode

from discord.ext import commands

from ..bot import ScottBot
from ..util.checks import nsfw
from ..util.messages import wait_for_deletion


class InternetCog(commands.Cog, name="Internet"):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.command(name="youtube", brief="Search YouTube", aliases=("yt",))
    async def _yt_search(self, ctx: commands.Context, *search_term: str):
        """
        Searches YouTube for the given search term and returns a random result

        Usage:
            {prefix}youtube <search term>

        Example:
            {prefix}youtube funny cats
        """
        search_term = ' '.join(search_term)
        if self.bot.http_session is not None:
            query_string = urlencode({"search_query": search_term})
            async with ctx.channel.typing():
                async with self.bot.http_session.get("http://www.youtube.com/results?" + query_string) as r:
                    if r.status == 200:
                        text = await r.text()
                        search_results = re.findall(r'href=\"/watch\?v=(.{11})', text)
                        vid_id = random.choice(search_results)
                        await ctx.send("http://www.youtube.com/watch?v=" + vid_id)

    @_yt_search.error
    async def yt_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.errors.MissingRequiredArgument):
            await ctx.send('You must input a video to search for!')

    @commands.command(name="urbandictionary", brief="Defines a term using UrbanDictionary", aliases=("urban",))
    @commands.check(nsfw)
    async def _urban(self, ctx: commands.Context, *term: str):
        """
        Search UrbanDictionary for the given term. Must be in a nsfw channel to use this command

        Usage:
            {prefix}urban <search term>
        """
        headers = {
            'x-rapidapi-host': "mashape-community-urban-dictionary.p.rapidapi.com",
            'x-rapidapi-key': "969f01b839msh4787708f5bcb9acp155a3djsn11ba69cd6ced"
        }
        term = ' '.join(term)
        if self.bot.http_session is not None:
            message = None
            async with ctx.channel.typing():
                async with self.bot.http_session.get("https://mashape-community-urban-dictionary.p.rapidapi.com/define",
                                                     headers=headers, params={"term": term}) as r:
                    if r.status == 200:
                        js = await r.json()
                        definition = random.choice(js["list"]) if term.lower() != "scott" else js["list"][4]
                        text = f'''```"{definition["word"]}" Definition:


{definition["definition"]}


Example:


{definition["example"]}


Author: {definition["author"]}
Likes: {definition["thumbs_up"]}```'''
                        text = text.replace("]", "").replace("[", "")
                        message = await ctx.send(text)
            if message is not None:
                await wait_for_deletion(message, (ctx.author,), client=self.bot)


def setup(bot: ScottBot):
    bot.add_cog(InternetCog(bot))
