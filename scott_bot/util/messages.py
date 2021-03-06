import asyncio
import contextlib
from typing import Optional, Sequence, Dict

import aiohttp
from discord import Client, Member, Message, Reaction, User, DiscordException
from discord.ext.commands import Context, BadArgument, Cog, Group, Command, MissingPermissions

from .constants import Emojis, IFTTT


async def wait_for_deletion(
        message: Message,
        users: Sequence[User],
        deletion_emojis: Sequence[str] = (Emojis.delete,),
        timeout: float = 60 * 5,
        attach_emojis: bool = True,
        client: Optional[Client] = None
) -> None:
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


async def bad_arg_error(cog: Optional[Cog], ctx: Context, error: DiscordException):
    if isinstance(error, BadArgument):
        await ctx.send(str(error.args[0]))
    else:
        raise error


async def missing_perms_error(cog: Optional[Cog], ctx: Context, error: DiscordException):
    print("miss perms")
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't have permission do that!")
    else:
        raise error


def get_cog_commands(cog: Cog, include_hidden=False) -> Dict[str, Command]:
    commands = {}
    for command in cog.get_commands():
        hidden = command.hidden if not include_hidden else False
        if not hidden:
            commands[command.name] = command
        if isinstance(command, Group):
            commands.update(get_group_commands(command))
    return commands


def get_group_commands(group: Group, name: str = None) -> Dict[str, Command]:
    name = name or group.name
    commands = {}
    for command in group.commands:
        if command.hidden:
            continue
        new_name = name + " " + command.name
        if isinstance(command, Group):
            commands.update(get_group_commands(command, new_name))
        elif isinstance(command, Command):
            commands[new_name] = command
    return commands


async def ifttt_notify(session: aiohttp.ClientSession, data: Sequence, name="None",
                       key=IFTTT.token):
    await session.post(
        f"https://maker.ifttt.com/trigger/{name}/with/key/{key}",
        data=dict(zip(('value1', 'value2', 'value3'), data)))
