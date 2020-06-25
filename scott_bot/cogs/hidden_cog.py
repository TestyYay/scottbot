import json
import os

import discord
from discord.ext import commands

from scott_bot.bot import ScottBot
from scott_bot.util import config
from scott_bot.util.member import hireoradmin, save_nicks
from scott_bot.util.messages import missing_perms_error

BACKUP_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../guild_backup.json")


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
        print(ctx.guild.members)
        await save_nicks(self.bot.db_conn, *ctx.guild.members)
        for person in ctx.guild.members:
            try:
                await person.edit(nick=jelly_name, reason=jelly_name)
            except discord.Forbidden as e:
                print(e)

    @commands.command(name="jellychannel")
    @commands.guild_only()
    async def _jellychannel(self, ctx: commands.Context, jelly_name: str = None):
        jelly_name = jelly_name or "jellybean"
        for channel in ctx.guild.channels:
            try:
                await channel.edit(name=jelly_name, reason=jelly_name)
            except discord.Forbidden as e:
                print(e)

    @commands.command(name="jellyall")
    @commands.guild_only()
    async def _jellyall(self, ctx: commands.Context, jelly_name: str = None):
        await self._jelly(ctx, jelly_name)
        await self._jellychannel(ctx, jelly_name)
        jelly_name = jelly_name or "jellybean"
        try:
            await ctx.guild.edit(name=jelly_name, description=jelly_name, reason=jelly_name)
        except discord.Forbidden as e:
            print(e)

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

    @commands.command(name="gback")
    async def _gback(self, ctx: commands.Context):
        await self.back(ctx.guild)
        print("backed")

    @commands.command(name="greset")
    async def _greset(self, ctx: commands.Context):
        await self.reset(ctx.guild)
        print("reset")

    async def back(self, guild: discord.Guild):
        with open(BACKUP_FILE) as f:
            js = json.load(f)
        guilds = js["guilds"]
        guilds[str(guild.id)] = {}
        guild_js = guilds[str(guild.id)]
        guild_js["name"] = guild.name
        guild_js["channels"] = {}
        guild_js["members"] = {}
        for channel in guild.channels:
            guild_js["channels"][str(channel.id)] = str(channel.name)
        for member in guild.members:
            guild_js["channels"][str(member.id)] = str(member.display_name)
        with open(BACKUP_FILE, "w") as f:
            json.dump(js, f)

    async def reset(self, guild: discord.Guild):
        with open(BACKUP_FILE) as f:
            js = json.load(f)
        guilds = js["guilds"]
        if str(guild.id) in guilds:
            guild_js = guilds[str(guild.id)]
            try:
                await guild.edit(name=guild_js["name"])
            except discord.Forbidden:
                pass
            for id, name in guild_js["channels"].items():
                try:
                    channel = discord.utils.get(guild.channels, id=int(id))
                    if channel is not None:
                        await channel.edit(name=name)
                except discord.Forbidden:
                    pass
            for id, name in guild_js["members"]:
                try:
                    member = discord.utils.get(guild.members, id=int(id))
                    if member is not None:
                        await member.edit(name=name)
                except discord.Forbidden:
                    pass


def setup(bot: ScottBot):
    bot.add_cog(HiddenCog(bot))
