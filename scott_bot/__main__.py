import yaml
from discord.ext import commands
from scott_bot.bot import ScottBot
from scott_bot.util import config

bot = ScottBot(command_prefix=config.Bot.default_prefix, description='ScottBot', case_insensitive=True)

bot.remove_command("help")

extensions = [
    "cogs.status_cog",
    "cogs.help_cog",
    "cogs.config_cog"
]


@bot.event
async def on_ready():
    print('Logged in as:')
    print(bot.user)
    print(bot.user.id)
    print('-' * len(str(bot.user.id)))
    for extension in extensions:
        bot.load_extension(extension)
    await bot.get_cog('Status').start_status_change()


@bot.event
async def on_message(message):
    if message.author.id == 696495244111380551:
        return
    await bot.process_commands(message)


@bot.command(
    name='test',
    description='This is a help test',
    brief='This is a help test',
    aliases=[],
    hidden=False
)
async def test(ctx: commands.Context, i: int, s: str = None):
    if s:
        await ctx.send(s)
    else:
        await ctx.send('.')


@bot.command(
    name='test2',
    description='This is a help test',
    brief='This is a help test',
    aliases=[],
    hidden=False
)
async def test2(ctx: commands.Context, *, x, s="hi"):
    await ctx.send(x)
    await ctx.send(s)


if __name__ == "__main__":
    bot.run(config.Bot.token)
