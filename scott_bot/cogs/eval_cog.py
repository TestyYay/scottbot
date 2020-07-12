import contextlib
import inspect
import pprint
import re
import textwrap
import traceback
import typing as t
from io import StringIO

import discord
from discord.ext import commands

from ..bot import ScottBot


class EvalCog(commands.Cog, name="Eval"):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self.env = {}
        self.stdout = StringIO()

    def _format(self, out: t.Any) -> t.Tuple[str, t.Optional[discord.Embed]]:
        """Format the eval output into a string & attempt to format it into an Embed."""
        self._ = out

        res = ""

        # Get all non-empty lines

        self.stdout.seek(0)
        text = self.stdout.read()
        self.stdout.close()
        self.stdout = StringIO()

        if text:
            res += (text + "\n")

        if out is None:
            # No output, return the input statement
            res = (res or "No Output", None)
        else:
            if isinstance(out, discord.Embed):
                # We made an embed? Send that as embed
                res += "<Embed>"
                res = (res, out)

            else:
                if isinstance(out, str) and out.startswith("Traceback (most recent call last):\n"):
                    # Leave out the traceback message
                    pretty = "\n" + "\n".join(out.split("\n")[3:])
                else:
                    pretty = pprint.pformat(out, compact=True, width=60)

                if pretty != str(out):
                    # We're using the pretty version, start on the next line
                    res += "\n"

                if pretty.count("\n") > 20:
                    # Text too long, shorten
                    li = pretty.split("\n")

                    pretty = ("\n".join(li[:3])  # First 3 lines
                              + "\n ...\n"  # Ellipsis to indicate removed lines
                              + "\n".join(li[-3:]))  # last 3 lines

                # Add the output
                res += pretty
                res = (res, None)

        return res  # Return (text, embed)

    async def _eval(self, ctx: commands.Context, code: str) -> None:
        """Eval the input code string & send an embed to the invoking context."""

        self.env = {
            "env": self.env,
            "contextlib": contextlib,
            "inspect": inspect,
            "stdout": self.stdout,
            "message": ctx.message,
            "author": ctx.message.author,
            "channel": ctx.channel,
            "guild": ctx.guild,
            "ctx": ctx,
            "self": self,
            "bot": self.bot,
            "discord": discord,
        }

        # Ignore this code, it works
        code_ = """
async def func():  # (None,) -> Any
    try:
        with contextlib.redirect_stdout(stdout):
{0}
        if '_' in locals():
            if inspect.isawaitable(_):
                _ = await _
            return _
    finally:
        env.update(locals())
""".format(textwrap.indent(code, '            '))

        try:
            exec(code_, self.env)  # noqa: B102,S102
            func = self.env['func']
            res = await func()

        except Exception:
            res = traceback.format_exc()
        # print(self.env)

        out, embed = self._format(res)
        await ctx.send(f"```py\n{out}```", embed=embed)

    @commands.command(name='eval', aliases=('e',))
    async def eval(self, ctx: commands.Context, *, code: str) -> None:
        """Run eval in a REPL-like format."""
        owner = await self.bot.application_info()
        owner = (owner.owner,)
        if ctx.author not in owner:
            return
        code = code.strip("`")
        if re.match('py(thon)?\n', code):
            code = "\n".join(code.split("\n")[1:])

        if not re.search(
                r"^(return|import|for|while|def|class|"
                r"from|exit|[a-zA-Z0-9]+\s*=)", code, re.M) and len(
            code.split("\n")) == 1:
            code = "_ = " + code

        await self._eval(ctx, code)


def setup(bot: ScottBot):
    bot.add_cog(EvalCog(bot))
