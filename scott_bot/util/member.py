from discord.ext.commands import Context


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
