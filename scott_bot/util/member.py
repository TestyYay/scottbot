from typing import Optional

import asyncpg
import discord
from discord.ext.commands import Context

from scott_bot.util import config


async def kicplayer(ctx: Context, person):
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


INSERT_SQL = """
INSERT INTO {tablename} (guild_id, user_id, nick)
    VALUES {vals};
"""


async def save_nicks(db_conn: Optional[asyncpg.Connection], *members: discord.Member):
    if db_conn is not None:
        template_vals = ", ".join(["($1, $2, $3)"] * len(members))
        vals = []
        for member in members:
            vals += [member.guild.id, member.id, member.display_name]
        await db_conn.execute(
            INSERT_SQL.format(tablename=config.DataBase.nickname_tablename, vals=template_vals),
            *vals
        )


def hire(user1: discord.Member, user2: discord.Member):
    return user1.top_role.position > user2.top_role.position


def hireoradmin(channel, user1, user2):
    x = hire(user1, user2)
    print("hir")
    print(x)
    print(user2.permissions_in(channel).administrator)
    return x and not user2.permissions_in(channel).administrator
