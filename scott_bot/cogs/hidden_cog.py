from discord.ext import commands

from scott_bot.bot import ScottBot
from scott_bot.util.member import hireoradmin, save_nicks
from scott_bot.util.messages import missing_perms_error


class HiddenCog(commands.Cog, name="Hidden", command_attrs=dict(hidden=True)):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self._nickall.error(missing_perms_error)

    @commands.command(name="nickall")
    async def _nickall(self, ctx: commands.Context):
        values = [person for person in ctx.guild.members if hireoradmin(ctx.channel, ctx.guild.me, person)]
        random.shuffle(values)
        member_dict = dict(zip(values, values[1:] + [values[0]]))

        await save_nicks(self.bot.db_conn, values)

        for person1, person2 in member_dict.items():
            try:
                await person1.edit(nick=person2.display_name)
            except commands.MissingPermissions:
                print(f"Could not change {person1.display_name}'s nickname")


def setup(bot: ScottBot):
    bot.add_cog(HiddenCog(bot))
