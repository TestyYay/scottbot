from datetime import datetime
from typing import Optional, Sequence

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


async def save_nicks(db_conn: Optional[asyncpg.Connection], *members: Sequence[discord.Member]):
    if db_conn is not None:
        template_vals = ", ".join(f"(${i}, ${i + 1}, ${i + 2}, ${i + 3})" for i in range(1, len(members) * 4, 4))
        vals = []
        for member in members:
            vals += [member.guild.id, member.id, member.display_name, datetime.now()]
        print(template_vals)
        print(vals)
        s = INSERT_SQL.format(tablename=config.DataBase.nickname_tablename, vals=template_vals)
        print(s)
        await db_conn.execute(
            s,
            *vals
        )


def hire(user1: discord.Member, user2: discord.Member):
    return user1.top_role.position > user2.top_role.position


def hireoradmin(channel, user1, user2):
    x = hire(user1, user2)
    return x and not user2.permissions_in(channel).administrator
