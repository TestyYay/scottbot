import asyncio
import random
import typing as t
from datetime import datetime

import discord
from discord.ext import commands

from ..bot import ScottBot
from ..util.constants import Bot
from ..util.converters import Expiry


class GiveawayCog(commands.Cog):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self.bot.loop.create_task(self.restart_giveaways())

    async def restart_giveaways(self):
        await self.bot.wait_until_ready()
        if self.bot.db_conn is not None:
            vals = await self.bot.db_conn.fetch(
                "SELECT message_id, channel_id, text, timeout, max_entries FROM giveaways")
            for val in vals:
                self.bot.loop.create_task(
                    self.restart_giveaway(val["message_id"], val["channel_id"], val["text"], val["timeout"]))

    async def restart_giveaway(self, message_id: int, channel_id: int, text: str, timeout: datetime):
        now = datetime.now()
        if timeout > now:
            await asyncio.sleep((timeout - now).total_seconds())
        channel = self.bot.get_channel(channel_id)
        await self.end_giveaway(text, channel, channel.members, message_id)

    @commands.command(name="giveaway", brief="Start a giveaway")
    async def _giveaway(self, ctx: commands.Context, item: str, max_time: Expiry, max_entries: int = None):
        """
        Start a giveaway!

        Usage:
            {prefix}giveaway <item> <timeout>
            {prefix}giveaway <item> <timeout> <max entries>

        Example:
            {prefix}giveaway "Discord Nitro" 1d
            {prefix}giveaway "Potato" 10 minutes 14
        """
        now = datetime.now()
        embed = discord.Embed(title="Giveaway Time! :tada:", color=Bot.color)
        embed.description = f"Enter to win **```\n{item}```**\nThis will end at **{max_time}**"
        if max_entries is not None:
            embed.description += f",\n or after **{max_entries}** entries"
        embed.description += "\nReact with :tada: to enter"
        message = await ctx.send(embed=embed)
        await message.add_reaction(u"\U0001F389")
        if self.bot.db_conn is not None:
            await self.bot.db_conn.execute("""
                                           INSERT INTO giveaways (message_id, channel_id, text, timeout, max_entries)
                                           VALUES (
                                               $1,
                                               $2,
                                               $3,
                                               $4,
                                               $5
                                           )
                                           ON CONFLICT ON CONSTRAINT giveaways_pkey
                                           DO NOTHING;""",
                                           message.id,
                                           ctx.channel.id,
                                           item,
                                           max_time,
                                           max_entries)
        difference = max_time - now
        await asyncio.sleep(difference.total_seconds())
        await self.end_giveaway(item, ctx.channel, ctx.guild.members, message.id)

    @commands.Cog.listener("on_reaction_add")
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        print("reaction_add")
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
        print("reaction remove")
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
