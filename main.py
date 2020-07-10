from discord.ext.commands import Context

import scott_bot.util.constants
from scott_bot.bot import ScottBot
from scott_bot.util import config

bot = ScottBot(command_prefix=config.prefix_for, description='ScottBot', case_insensitive=True)

bot.remove_command("help")


@bot.command(name="test", hidden=True)
async def test(ctx: Context):
    _channel = await config.get_config("admin_channel", bot, ctx.guild)
    if _channel is not None:
        typ = await _channel.get_type()
        print(typ)


if __name__ == "__main__":
    bot.run(scott_bot.util.constants.Bot.token)
