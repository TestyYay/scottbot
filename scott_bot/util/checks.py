from discord.ext.commands import Context, check


def nsfw(*args):
    print(args)

    async def predicate(ctx: Context):
        return ctx.channel.is_nsfw()

    return check(predicate)
