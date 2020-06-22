import discord
from discord.ext import commands
from psycopg2 import sql

from scott_bot.bot import ScottBot
from scott_bot.util.config import IFTTT, DataBase
from scott_bot.util.messages import ifttt_notify

SUGGESTION_SQL = """INSERT INTO {tablename} (user_id, user_name, suggestion_text)
VALUES (
    $1,
    $2,
    $3
);"""


class SuggestionCog(commands.Cog, name="Suggestion"):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.command(name="suggest", brief="Provide feedback")
    @commands.cooldown(2, 60, commands.BucketType.user)
    async def _suggest(self, ctx: commands.Context, *suggestion: str):
        """
        Send a suggestion to the maker of this bot.

        Usage:
            {prefix}suggest <suggestion>
        Example:
            {prefix}suggest git gud lol
        """
        if not ctx.guild:
            suggestion = ' '.join(suggestion)
            if suggestion:
                if self.bot.http_session is not None:
                    await ifttt_notify(self.bot.http_session, (suggestion, ctx.author.name), name=IFTTT.suggestion)
                embed = discord.Embed()
                if self.bot.db_conn is not None:
                    x = await self.bot.db_conn.execute(
                        SUGGESTION_SQL.format(tablename=sql.Identifier(DataBase.suggestions_tablename)),
                        ctx.author.id,
                        ctx.author.display_name,
                        suggestion
                    )
                    print(x)
                    print(dir(x))
                    embed.add_field(name='Your response has been recorded', value='Thank you for your feedback!')
                else:
                    embed.add_field(name='An error has occured', value='Please try again later.')
                await ctx.author.send(embed=embed)
            else:
                await ctx.send('Use the syntax: //suggest <suggestion.')
        else:
            await ctx.send('Please send feedback via dm. Thank You!')
            await ctx.author.send('Please send feedback here. Thank You!')

    # @_suggest.error
    # async def on_cooldown(self, ctx, error):
    #     print(error)
    #     if isinstance(error, commands.CommandOnCooldown):
    #         embed = discord.Embed(title="You are on cooldown", description="Please try this again later")
    #         await ctx.author.send(embed=embed)


def setup(bot: ScottBot):
    bot.add_cog(SuggestionCog(bot))
