import discord
from discord.ext import commands

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
        if not ctx.guild:
            suggestion = ' '.join(suggestion)
            if suggestion:
                if self.bot.http_session is not None:
                    await ifttt_notify(self.bot.http_session, (suggestion, ctx.author.name), name=IFTTT.suggestion)
                embed = discord.Embed()
                if self.bot.db_conn is not None:
                    await self.bot.db_conn.execute(
                        SUGGESTION_SQL.format(tablename=DataBase.suggestions_tablename),
                        ctx.author.id,
                        ctx.author.display_name,
                        suggestion
                    )
                    embed.add_field(name='Your response has been recorded', value='Thank you for your feedback!')
                else:
                    embed.add_field(name='An error has occured', value='Please try again later.')
                await ctx.author.send(embed=embed)
            else:
                await ctx.send('Use the syntax: //suggest <suggestion.')
        else:
            await ctx.send('Please send feedback via dm. Thank You!')
            await ctx.author.send('Please send feedback here. Thank You!')


def setup(bot: ScottBot):
    bot.add_cog(SuggestionCog(bot))
