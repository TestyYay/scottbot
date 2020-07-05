import asyncio
import random
import typing as t

import discord
from discord.ext import commands

from ..bot import ScottBot
from ..util.constants import Bot


class GiveawayCog(commands.Cog):
    def __init__(self, bot: ScottBot):
        self.bot = bot

    @commands.command(name="giveaway", brief="Start a giveaway")
    async def _giveaway(self, ctx: commands.Context, item: str, max_time: int = None, max_entries: int = None):
        """
        Start a giveaway!

        Usage:
            {prefix}giveaway <item>
            {prefix}giveaway <item> <timeout (secs)>
            {prefix}giveaway <item> <timeout (secs)> <max entries>

        Example:
            {prefix}giveaway "Discord Nitro"
            {prefix}giveaway "Potato" 86400
            {prefix}giveaway "death" 86400 14
        """
        embed = discord.Embed(title="Giveaway Time! :tada:", color=Bot.color)
        embed.description = f"Enter to win **{item}**"
        if max_time is not None:
            embed.description += f"\nThis will end after {max_time} seconds"
            if max_entries is not None:
                embed.description += f" or {max_entries} entries"
        elif max_entries is not None:
            embed.description += f"\nThis will end after {max_entries} entries"
        embed.description += "\nReact with :tada: to enter"
        if max_time is None and max_entries is None:
            return await ctx.send("`Please specify either the timeout or the max entries`")
        message = await ctx.send(embed=embed)
        await message.add_reaction(u"\U0001F389")
        if self.bot.db_conn is not None:
            await self.bot.db_conn.execute("""
                                           INSERT INTO giveaways (message_id, text, max_entries)
                                           VALUES (
                                               $1,
                                               $2,
                                               $3
                                           )
                                           ON CONFLICT ON CONSTRAINT giveaways_pkey
                                           DO NOTHING;""",
                                           message.id,
                                           item,
                                           max_entries)
        if max_time is not None:
            await asyncio.sleep(max_time)
            await self.end_giveaway(item, ctx.channel, ctx.guild.members, message.id)

    @commands.Cog.listener("on_reaction_add")
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        if self.bot.db_conn is not None and user.id != self.bot.user.id:
            val = await self.bot.db_conn.fetchrow("""
                                                  SELECT message_id, text, max_entries FROM giveaways
                                                  WHERE message_id = $1""",
                                                  reaction.message.id)
            if val is not None:
                await self.bot.db_conn.execute("""
                                               INSERT INTO giveaway_entries (message_id, user_id)
                                               VALUES (
                                                   $1,
                                                   $2
                                               )
                                               ON CONFLICT ON CONSTRAINT giveaway_entries_pkey
                                               DO NOTHING;""",
                                               reaction.message.id,
                                               user.id,
                                               )
                if val.get("max_entries") is not None:
                    entries = await self.bot.db_conn.fetch("""
                                                           SELECT message_id, user_id FROM giveaway_entries
                                                           WHERE message_id = $1;""",
                                                           reaction.message.id)
                    if len(entries) >= val.get("max_entries"):
                        await self.end_giveaway(val.get("text"), reaction.message.channel,
                                                reaction.message.guild.members,
                                                reaction.message.id)

    @commands.Cog.listener("on_reaction_remove")
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
        if self.bot.db_conn is not None and user.id != self.bot.user.id:
            if self.bot.db_conn is not None and user.id != self.bot.user.id:
                val = await self.bot.db_conn.fetchrow("""
                                                      SELECT message_id, text, max_entries FROM giveaways
                                                      WHERE message_id = $1""",
                                                      reaction.message.id)
                if val is not None:
                    await self.bot.db_conn.execute("""
                                                   DELETE FROM giveaway_entries
                                                   WHERE message_id = $1
                                                   AND user_id = $2""",
                                                   reaction.message.id,
                                                   user.id)

    async def end_giveaway(self, text: str, channel: discord.TextChannel, members: t.Sequence[discord.Member],
                           message_id: int):
        if self.bot.db_conn is not None:
            users = await self.bot.db_conn.fetch("SELECT user_id FROM giveaway_entries WHERE message_id = $1",
                                                 message_id)
            if users is not None:
                usrs = []
                for user in users:
                    user = discord.utils.get(members, id=user.get("user_id"))
                    if user is not None:
                        usrs.append(user)
                if len(users) > 0:
                    user = random.choice(usrs)
                    embed = discord.Embed(title="Giveaway Winner! :tada:", color=Bot.color)
                    embed.description = f"{user.mention} has won **{text}** in the giveaway! Congrats!"
                    await channel.send(embed=embed)
                    if self.bot.db_conn is not None:
                        await self.bot.db_conn.execute(
                            "DELETE FROM giveaways WHERE message_id = $1;",
                            message_id)
                        await self.bot.db_conn.execute(
                            "DELETE FROM giveaway_entries WHERE message_id = $1;",
                            message_id)


def setup(bot: ScottBot):
    bot.add_cog(GiveawayCog(bot))
