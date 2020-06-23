from scott_bot.bot import ScottBot
from scott_bot.util import config

bot = ScottBot(command_prefix=config.prefix_for, description='ScottBot', case_insensitive=True)

bot.remove_command("help")

extensions = [
    "cogs.status_cog",
    "cogs.help_cog",
    "cogs.admin_cog",
    "cogs.join_cog",
    "cogs.dad_cog",
    "cogs.internet_cog",
    "cogs.fun_cog",
    "cogs.hidden_cog"
    "cogs.other_cog"
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


# @bot.event
# async def on_message(message):
#     if message.author.id == 696495244111380551:
#         return
#     await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(config.Bot.token)
