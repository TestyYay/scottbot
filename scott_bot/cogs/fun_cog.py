import random

import discord
from discord.ext import commands

from scott_bot.bot import ScottBot
from scott_bot.util.config import UwU
from scott_bot.util.member import save_nicks
from scott_bot.util.messages import missing_perms_error


class FunCog(commands.Cog, name="Fun"):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self._kick.error(missing_perms_error)

    @commands.command(name="uwu", brief="Uwuify the provided text")
    async def _uwu(self, ctx: commands.Context, *text: str):
        """
        Uwuifies the provided text and adds a random lenny face to the end.

        Usage:
            {prefix}uwu <text>
        """
        text = " ".join(text)
        for key, value in UwU.replaces.items():
            text = text.replace(key, value)
        await ctx.send(text + ' ' + random.choice(UwU.faces))

    @commands.command(name="trebuchet", brief="Trebuchet = good")
    async def _trebuchet(self, ctx: commands.Context):
        msg = '''A trebuchet (French trébuchet) is a type of catapult that uses a swinging arm to throw a projectile. It was a common powerful siege engine until the advent of gunpowder.
There are two main types of trebuchets.  The first is the traction trebuchet, or mangonel, which uses manpower to swing the arm. It first appeared in China in the 4th century BC. Carried westward by the Avars, the technology was adopted by the Byzantines in the late 6th century AD and by their neighbors in the following centuries.
The later, and often larger, counterweight trebuchet, also known as the counterpoise trebuchet, uses a counterweight to swing the arm. It appeared in both Christian and Muslim lands around the Mediterranean in the 12th century, and made its way back to China via Mongol conquests in the 13th century.'''
        await ctx.send(msg)

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

    @commands.command(name="nickswitch", brief="Swap two player's nicks!", aliases=("nick", "nickswap"))
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
    async def _nic(self, ctx: commands.Context, member1: discord.Member = None, member2: discord.Member = None):
        bot_user = ctx.guild.me
        guild_members = [member for member in ctx.guild.members if
                         hireoradmin(ctx.guild, ctx.channel, bot_user, member)]
        if member1 is not None and member2 is None:
            guild_members.remove(member1)
            member2 = random.choice(guild_members)
        elif member1 is None and member2 is None:
            member1 = random.choice(guild_members)
            guild_members.remove(member1)
            member2 = random.choice(guild_members)
        await save_nicks(self.bot.db_conn, member1, member2)
        await _swap_nicks(member1, member2)
        await ctx.send('Nicknames changed')


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


async def _swap_nicks(person1: discord.Member, person2: discord.Member):
    n1 = person1.display_name
    n2 = person2.display_name
    await person2.edit(nick=n1)
    await person1.edit(nick=n2)
    print(person1.display_name + '  >>>>>  ' + person2.display_name)
    print(person2.display_name + '  >>>>>  ' + person1.display_name)


def setup(bot: ScottBot):
    bot.add_cog(FunCog(bot))
