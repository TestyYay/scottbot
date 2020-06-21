from discord.ext.commands import Context


def nsfw(ctx: Context):
    return ctx.channel.is_nsfw()
