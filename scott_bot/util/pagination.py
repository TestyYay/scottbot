import asyncio
import typing as t

import discord
from discord.abc import User
from discord.ext.commands import Context, Cog, Command

from scott_bot.util.config import Emojis
from scott_bot.util.messages import wait_for_deletion, get_cog_commands

PAGINATION_EMOJI = (Emojis.first, Emojis.left, Emojis.delete, Emojis.right, Emojis.last)


class EmptyPaginatorEmbed(Exception):
    """Raised when attempting to paginate with empty contents."""

    pass


class HelpPaginator:

    def __init__(self) -> None:
        self.pages: t.List[str] = []
        self._current_page = None

    @classmethod
    async def paginate(
            cls,
            ctx: Context,
            embed: discord.Embed,
            cogs: t.Optional[t.Sequence[Cog]] = None,
            pages: t.Optional[t.Sequence[str]] = None,
            timeout: int = 300,
            restrict_to_users: t.Optional[t.Sequence[User]] = None,
            footer_text: str = None
    ) -> t.Optional[discord.Message]:

        def event_check(reaction_: discord.Reaction, user_: discord.Member) -> bool:
            """Make sure that this reaction is what we want to operate on."""

            no_restrictions = (
                not restrict_to_users
                or user_.id in [usr.id for usr in restrict_to_users]
            )

            return (
                # Conditions for a successful pagination:
                all((
                    # Reaction is on this message
                    reaction_.message.id == message.id,
                    # Reaction is one of the pagination emotes
                    str(reaction_.emoji) in PAGINATION_EMOJI,
                    # Reaction was not made by the Bot
                    user_.id != ctx.bot.user.id,
                    # The user is correct
                    no_restrictions
                ))
            )

        def _get_help_list(commands):
            if len(commands) <= 0:
                return "[There are no commands under this category]"
            i = max(len(x) for x in commands)
            s = ""
            for name, command in commands.items():
                s += f"{name:{i}} : {command.brief}\n"
            return s

        def set_footer(footer: t.Optional[str], paginator: HelpPaginator, embed: discord.Embed) -> None:
            if footer:
                embed.set_footer(text=f"{footer} (Page {paginator.page_num + 1}/{len(paginator.pages)})")
            else:
                embed.set_footer(text=f"Page {paginator.page_num + 1}/{len(paginator.pages)}")

        async def change_page(page_num, reaction: discord.Reaction, paginator: HelpPaginator,
                              embed: discord.Embed) -> None:
            message = reaction.message
            await message.remove_reaction(reaction.emoji, user)
            paginator.page_num = page_num

            # log.debug(f"Got first page reaction - changing to page 1/{len(paginator.pages)}")

            # embed.description = ""
            # await message.edit(embed=embed)
            embed.description = paginator.page
            set_footer(footer_text, paginator, embed)
            await message.edit(embed=embed)

        paginator = cls()

        if cogs is not None:
            for cog in cogs:
                comms = get_cog_commands(cog)
                help_page = f"""**```asciidoc
{cog.qualified_name}
{'-' * len(cog.qualified_name)}
        
{_get_help_list(comms)}```**"""
                paginator.add_page(help_page)

        elif pages is not None:
            for page in pages:
                paginator.add_page(page)

        embed.description = paginator.page

        if len(paginator.pages) <= 1:
            if footer_text:
                embed.set_footer(text=footer_text)
                # log.trace(f"Setting embed footer to '{footer_text}'")

            # log.debug("There's less than two pages, so we won't paginate - sending single page on its own")
            message = await ctx.send(embed=embed)
            await wait_for_deletion(message, restrict_to_users, client=ctx.bot)
            return message
        else:
            set_footer(footer_text, paginator, embed)
            # log.trace(f"Setting embed footer to '{embed.footer.text}'")

            # log.debug("Sending first page to channel...")
            message = await ctx.send(embed=embed)
        for emoji in PAGINATION_EMOJI:
            # Add all the applicable emoji to the message
            # log.trace(f"Adding reaction: {repr(emoji)}")
            await message.add_reaction(emoji)

        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=event_check)
                # log.trace(f"Got reaction: {reaction}")
            except asyncio.TimeoutError:
                # log.debug("Timed out waiting for a reaction")
                break  # We're done, no reactions for the last 5 minutes

            if reaction.emoji == Emojis.delete:
                # log.debug("Got delete reaction")
                return await message.delete()

            if reaction.emoji == Emojis.first:
                await change_page(0, reaction, paginator, embed)

            if reaction.emoji == Emojis.last:
                await change_page(len(paginator.pages) - 1, reaction, paginator, embed)

            if reaction.emoji == Emojis.left:

                if paginator.page_num > 0:
                    await change_page(paginator.page_num - 1, reaction, paginator, embed)
                else:
                    await message.remove_reaction(reaction.emoji, user)

            if reaction.emoji == Emojis.right:
                await message.remove_reaction(reaction.emoji, user)

                if paginator.page_num < len(paginator.pages) - 1:
                    await change_page(paginator.page_num + 1, reaction, paginator, embed)

    def add_page(self, page: str):
        self.pages.append(page)

    def _get_help_list(self, commands: t.Sequence[Command]):
        i = max(len(x.name) for x in self.bot.commands)
        s = ""
        for command in commands:
            s += f"{command.name:{i}} : {command.brief}\n"
        return s

    @property
    def page_num(self):
        if self._current_page is None and len(self.pages) > 0:
            self._current_page = 0
        return self._current_page

    @page_num.setter
    def page_num(self, page: int):
        self._current_page = max(0, min(page, len(self.pages) - 1))

    @property
    def page(self):
        return (
            "" if self.page_num is None
            else self.pages[self.page_num]
        )