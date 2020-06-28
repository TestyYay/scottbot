from discord.ext.commands import Context

from scott_bot.bot import ScottBot
from scott_bot.util import config

bot = ScottBot(command_prefix=config.prefix_for, description='ScottBot', case_insensitive=True)

bot.remove_command("help")

extensions = [
    "status_cog",
    "help_cog",
    "admin_cog",
    "join_cog",
    "dad_cog",
    "internet_cog",
    "fun_cog",
    "hidden_cog",
    "spam_cog",
    "other_cog"
]


@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user)
    print(bot.user.id)
    print('-' * len(str(bot.user.id)))
    for extension in extensions:
        bot.load_extension("scott_bot.cogs." + extension)
    await bot.get_cog('Status').start_status_change()


@bot.command(name="test", hidden=True)
async def test(ctx: Context):
    _channel = await config.get_config("admin_channel", bot, ctx.guild)
    if _channel is not None:
        typ = await _channel.get_type()
        print(typ)


if __name__ == "__main__":
    bot.run(config.Bot.token)
