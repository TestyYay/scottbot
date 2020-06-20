import asyncio
import logging
import typing as t
from contextlib import suppress

import discord
from discord.abc import User
from discord.ext.commands import Context, Paginator, Cog, Command, Group

from scott_bot.util.config import Emojis
from scott_bot.util.messages import wait_for_deletion, get_cog_commands, get_group_commands


PAGINATION_EMOJI = (Emojis.first, Emojis.left, Emojis.right, Emojis.last, Emojis.delete)


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
            i = max(len(x.name) for x in commands)
            s = ""
            for command in commands:
                s += f"{command.name:{i}} : {command.brief}\n"
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

            embed.description = ""
            await message.edit(embed=embed)
            embed.description = paginator.page
            set_footer(footer_text, paginator, embed)
            await message.edit(embed=embed)

        paginator = cls()

        if cogs is not None:
            for cog in cogs:
                help_page = f"""**```asciidoc
    {cog.qualified_name}
    {'-' * len(cog.qualified_name)}
        
    {_get_help_list(get_cog_commands(cog))}```**"""
                paginator.add_page(help_page)

            paginator.page_num = 0

            embed.description = paginator.page
        elif pages is not None:
            for page in pages:
                paginator.add_page(page)

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


class LinePaginator(Paginator):
    """
    A class that aids in paginating code blocks for Discord messages.
    Available attributes include:
    * prefix: `str`
        The prefix inserted to every page. e.g. three backticks.
    * suffix: `str`
        The suffix appended at the end of every page. e.g. three backticks.
    * max_size: `int`
        The maximum amount of codepoints allowed in a page.
    * max_lines: `int`
        The maximum amount of lines allowed in a page.
    """

    def __init__(
            self, prefix: str = '```', suffix: str = '```', max_size: int = 2000, max_lines: int = None
    ) -> None:
        """
        This function overrides the Paginator.__init__ from inside discord.ext.commands.
        It overrides in order to allow us to configure the maximum number of lines per page.
        """
        self.prefix = prefix
        self.suffix = suffix
        self.max_size = max_size - len(suffix)
        self.max_lines = max_lines
        self._current_page = [prefix]
        self._linecount = 0
        self._count = len(prefix) + 1  # prefix + newline
        self._pages = []

    def add_line(self, line: str = '', *, empty: bool = False) -> None:
        """
        Adds a line to the current page.
        If the line exceeds the `self.max_size` then an exception is raised.
        This function overrides the `Paginator.add_line` from inside `discord.ext.commands`.
        It overrides in order to allow us to configure the maximum number of lines per page.
        """
        if len(line) > self.max_size - len(self.prefix) - 2:
            raise RuntimeError('Line exceeds maximum page size %s' % (self.max_size - len(self.prefix) - 2))

        if self.max_lines is not None:
            if self._linecount >= self.max_lines:
                self._linecount = 0
                self.close_page()

            self._linecount += 1
        if self._count + len(line) + 1 > self.max_size:
            self.close_page()

        self._count += len(line) + 1
        self._current_page.append(line)

        if empty:
            self._current_page.append('')
            self._count += 1

    @classmethod
    async def paginate(
            cls,
            lines: t.List[str],
            ctx: Context,
            embed: discord.Embed,
            prefix: str = "",
            suffix: str = "",
            max_lines: t.Optional[int] = None,
            max_size: int = 500,
            empty: bool = True,
            restrict_to_user: User = None,
            timeout: int = 300,
            footer_text: str = None,
            url: str = None,
            exception_on_empty_embed: bool = False,
    ) -> t.Optional[discord.Message]:
        """
        Use a paginator and set of reactions to provide pagination over a set of lines.
        The reactions are used to switch page, or to finish with pagination.
        When used, this will send a message using `ctx.send()` and apply a set of reactions to it. These reactions may
        be used to change page, or to remove pagination from the message.
        Pagination will also be removed automatically if no reaction is added for five minutes (300 seconds).
        Example:
        >>> embed = discord.Embed()
        >>> embed.set_author(name="Some Operation", url=url, icon_url=icon)
        >>> await LinePaginator.paginate([line for line in lines], ctx, embed)
        """

        def event_check(reaction_: discord.Reaction, user_: discord.Member) -> bool:
            """Make sure that this reaction is what we want to operate on."""
            no_restrictions = (
                # Pagination is not restricted
                    not restrict_to_user
                    # The reaction was by a whitelisted user
                    or user_.id == restrict_to_user.id
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
                    # There were no restrictions
                    no_restrictions
                ))
            )

        paginator = cls(prefix=prefix, suffix=suffix, max_size=max_size, max_lines=max_lines)
        current_page = 0

        if not lines:
            if exception_on_empty_embed:
                # log.exception("Pagination asked for empty lines iterable")
                raise EmptyPaginatorEmbed("No lines to paginate")

            # log.debug("No lines to add to paginator, adding '(nothing to display)' message")
            lines.append("(nothing to display)")

        for line in lines:
            try:
                paginator.add_line(line, empty=empty)
            except Exception:
                # log.exception(f"Failed to add line to paginator: '{line}'")
                raise  # Should propagate
                # log.trace(f"Added line to paginator: '{line}'")

        # log.debug(f"Paginator created with {len(paginator.pages)} pages")

        embed.description = paginator.pages[current_page]

        if len(paginator.pages) <= 1:
            if footer_text:
                embed.set_footer(text=footer_text)
                # log.trace(f"Setting embed footer to '{footer_text}'")

            if url:
                embed.url = url
                # log.trace(f"Setting embed url to '{url}'")

            # log.debug("There's less than two pages, so we won't paginate - sending single page on its own")
            return await ctx.send(embed=embed)
        else:
            if footer_text:
                embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
            else:
                embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")
            # log.trace(f"Setting embed footer to '{embed.footer.text}'")

            if url:
                embed.url = url
                # log.trace(f"Setting embed url to '{url}'")

            # log.debug("Sending first page to channel...")
            message = await ctx.send(embed=embed)

        # log.debug("Adding emoji reactions to message...")

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

            if str(reaction.emoji) == Emojis.delete:
                # log.debug("Got delete reaction")
                return await message.delete()

            if reaction.emoji == Emojis.first:
                await message.remove_reaction(reaction.emoji, user)
                current_page = 0

                # log.debug(f"Got first page reaction - changing to page 1/{len(paginator.pages)}")

                embed.description = ""
                await message.edit(embed=embed)
                embed.description = paginator.pages[current_page]
                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")
                await message.edit(embed=embed)

            if reaction.emoji == Emojis.last:
                await message.remove_reaction(reaction.emoji, user)
                current_page = len(paginator.pages) - 1

                # log.debug(f"Got last page reaction - changing to page {current_page + 1}/{len(paginator.pages)}")

                embed.description = ""
                await message.edit(embed=embed)
                embed.description = paginator.pages[current_page]
                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")
                await message.edit(embed=embed)

            if reaction.emoji == Emojis.left:
                await message.remove_reaction(reaction.emoji, user)

                if current_page <= 0:
                    # log.debug("Got previous page reaction, but we're on the first page - ignoring")
                    continue

                current_page -= 1
                # log.debug(f"Got previous page reaction - changing to page {current_page + 1}/{len(paginator.pages)}")

                embed.description = ""
                await message.edit(embed=embed)
                embed.description = paginator.pages[current_page]

                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")

                await message.edit(embed=embed)

            if reaction.emoji == Emojis.right:
                await message.remove_reaction(reaction.emoji, user)

                if current_page >= len(paginator.pages) - 1:
                    # log.debug("Got next page reaction, but we're on the last page - ignoring")
                    continue

                current_page += 1
                # log.debug(f"Got next page reaction - changing to page {current_page + 1}/{len(paginator.pages)}")

                embed.description = ""
                await message.edit(embed=embed)
                embed.description = paginator.pages[current_page]

                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")

                await message.edit(embed=embed)

        # log.debug("Ending pagination and clearing reactions.")
        with suppress(discord.NotFound):
            await message.clear_reactions()
