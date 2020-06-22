import asyncio
import random

import discord
from discord.ext import commands

from scott_bot.bot import ScottBot
from scott_bot.util.messages import missing_perms_error


class KickCog(commands.Cog, name="Kick"):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self._kick.error(missing_perms_error)

    @commands.command(name="randomkick", brief="Kick a random person")
    @commands.has_permissions(kick_members=True)
    async def _kick(self, ctx: commands.Context, member: discord.Member = None):
        print("in")
        if not member:
            bot_user = ctx.guild.get_member(bot.user.id)
            guild_members = ctx.guild.members.copy()

            guild_members.remove(ctx.author)
            guild_members.remove(bot_user)

            guild_members = [member for member in guild_members if not member.permissions_in(ctx.channel).administrator]
            member = random.choice(guild_members)

        await kicplayer(ctx, member)


async def _kicplayer(ctx: commands.Context, person: discord.Member):
    kickmsg = await ctx.send('Getting players')
    mems = ctx.guild.members
    for player in mems:
        if player != person:
            await asyncio.sleep(10 / len(mems))
            await kickmsg.edit(content='Found: {}'.format(player))
    await asyncio.sleep(10 / len(mems))
    await kickmsg.edit(content='Found: {}'.format(person))
    await asyncio.sleep(10 / len(mems))
    await kickmsg.edit(content='Kicking {}'.format(person))
    await asyncio.sleep(0.5)
    await person.send("You got randomly kicked from server \"{}\" by @{}.".format(ctx.guild.name, ctx.author))
    await person.send('Here is an invite link back.')
    invitelinknew = await ctx.channel.create_invite(max_uses=1, unique=True)
    await person.send(invitelinknew)
    await ctx.guild.kick(person)
    await asyncio.sleep(0.5)
    await kickmsg.edit(content='Kicked {}'.format(person))


def setup(bot: ScottBot):
    bot.add_cog(KickCog(bot))
