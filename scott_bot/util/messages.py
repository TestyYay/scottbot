import contextlib
from typing import Optional, Sequence

import asyncio
from discord import Client, Member, Message, Reaction, User, DiscordException
from discord.ext.commands import Context, BadArgument, Cog, Group
from discord.abc import Snowflake
from scott_bot.util.config import Emojis


async def wait_for_deletion(
        message: Message,
        users: Sequence[User],
        deletion_emojis: Sequence[str] = (Emojis.delete,),
        timeout: float = 60 * 5,
        attach_emojis: bool = True,
        client: Optional[Client] = None
) -> None:
    """
    Wait for up to `timeout` seconds for a reaction by any of the specified `user_ids` to delete the message.
    An `attach_emojis` bool may be specified to determine whether to attach the given
    `deletion_emojis` to the message in the given `context`
    A `client` instance may be optionally specified, otherwise client will be taken from the
    guild of the message.
    """
    if message.guild is None and client is None:
        raise ValueError("Message must be sent on a guild")

    bot = client or message.guild.me

    if attach_emojis:
        for emoji in deletion_emojis:
            await message.add_reaction(emoji)

    def check(reaction: Reaction, user: Member) -> bool:
        """Check that the deletion emoji is reacted by the appropriate user."""
        return (
                reaction.message.id == message.id
                and str(reaction.emoji) in deletion_emojis
                and user.id in [usr.id for usr in users]
        )

    with contextlib.suppress(asyncio.TimeoutError):
        await bot.wait_for('reaction_add', check=check, timeout=timeout)
        await message.delete()


async def bad_arg_error(cog: Cog, ctx: Context, error: DiscordException):
    if isinstance(error, BadArgument):
        await ctx.send(str(error.args[0]))


def get_group_commands(group: Group, name: str):
    print("getting group")
    commands = []
    for command in group.commands:
        new_name = name + " " + command.name
        if isinstance(command, Group):
            commands += get_group_commands(command, new_name)
        elif isinstance(command, Command):
            command.name = new_name
            commands.append(command)
    print(commands)
    return commands
