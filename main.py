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


# @bot.event
# async def on_message(message):
#     if message.author.id == 696495244111380551:
#         return
#     await bot.process_commands(message)


if __name__ == "__main__":
    bot.run(config.Bot.token)
