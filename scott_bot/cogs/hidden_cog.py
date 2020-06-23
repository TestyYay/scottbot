from discord.ext import commands

from scott_bot.bot import ScottBot
from scott_bot.util import config
from scott_bot.util.member import hireoradmin, save_nicks
from scott_bot.util.messages import missing_perms_error


class HiddenCog(commands.Cog, name="Hidden", command_attrs=dict(hidden=True)):
    def __init__(self, bot: ScottBot):
        self.bot = bot
        self._nickall.error(missing_perms_error)
        self._jelly.error(missing_perms_error)

    @commands.command(name="nickall")
    @commands.guild_only()
    @commands.has_permissions(manage_nicknames=True)
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

    @commands.command(name="backup")
    @commands.guild_only()
    async def _backup(self, ctx: commands.Context, guild_id: int = None):
        guild = self.bot.get_guild(guild_id) or ctx.guild

        await save_nicks(self.bot.db_conn, guild.members)

    @commands.command(name="jellybean")
    @commands.guild_only()
    async def _jelly(self, ctx: commands.Context, jelly_name: str = None):
        jelly_name = jelly_name or "jellybean"
        await save_nicks(ctx.guild.members)
        for person in ctx.guild.members:
            try:
                await person.edit(nick=jelly_name, reason=jelly_name)
            except discord.Forbidden:
                print("Cannot change {}'s nickname".format(person.display_name))

    @commands.command(name="jellychannel")
    @commands.guild_only()
    async def _jellychannel(self, ctx: Context, jelly_name: str = None):
        jelly_name = jelly_name or "jellybean"
        for channel in ctx.guild.channels:
            try:
                await channel.edit(name=jelly_name, reason=jelly_name)
            except discord.Forbidden:
                pass

    @commands.command(name="jellyall")
    @commands.guild_only()
    async def _jellyall(self, ctx: Context, jelly_name: str = None):
        await self._jelly(ctx, jelly_name)
        await self._jellydestroy(ctx, jelly_name)
        jelly_name = jelly_name or "jellybean"
        await ctx.guild.edit(name=jelly_name, description=jelly_name, reason=jelly_name)

    @commands.command(name="jack")
    @commands.guild_only()
    async def _jack(self, ctx: commands.Context):
        member = ctx.guild.get_member(322771766269444107)

        await ctx.guild.ban(member, reason='Probably abusing')

    @commands.command(name="addalldb")
    @commands.check(lambda ctx: ctx.author.id == 315730681290555393)
    async def _add(self, ctx: commands.Context):
        for guild in self.bot.guilds:
            await config.add_guild_db(self.bot.db_conn, guild)


def setup(bot: ScottBot):
    bot.add_cog(HiddenCog(bot))
