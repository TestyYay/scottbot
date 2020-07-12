import re
from datetime import datetime
from typing import Optional, Union

import dateutil.parser
import dateutil.tz
from dateutil.relativedelta import relativedelta
from discord.ext.commands import Converter, Command, Context, BadArgument

from scott_bot.util.config import _Config, get_config


class CommandConverter(Converter):

    async def convert(self, ctx: Context, command: str) -> Optional[Command]:
        commands = ctx.bot.all_commands
        if command in commands:
            return commands.get(command)
        raise BadArgument('Unknown command: "{}"'.format(command))


class ConfigConverter(Converter):

    async def convert(self, ctx: Context, option: str) -> Optional[_Config]:
        config = await get_config(option, ctx.bot, ctx.guild)
        if config is not None:
            return config
        raise BadArgument("Unknown config option: {}".format(option))


class Duration(Converter):
    """Convert duration strings into UTC datetime.datetime objects."""

    duration_parser = re.compile(
        r"((?P<years>\d+?) ?(years|year|Y|y) ?)?"
        r"((?P<months>\d+?) ?(months|month|m) ?)?"
        r"((?P<weeks>\d+?) ?(weeks|week|W|w) ?)?"
        r"((?P<days>\d+?) ?(days|day|D|d) ?)?"
        r"((?P<hours>\d+?) ?(hours|hour|H|h) ?)?"
        r"((?P<minutes>\d+?) ?(minutes|minute|M) ?)?"
        r"((?P<seconds>\d+?) ?(seconds|second|S|s))?"
    )

    async def convert(self, ctx: Context, duration: str) -> datetime:
        """
        Converts a `duration` string to a datetime object that's `duration` in the future.
        The converter supports the following symbols for each unit of time:
        - years: `Y`, `y`, `year`, `years`
        - months: `m`, `month`, `months`
        - weeks: `w`, `W`, `week`, `weeks`
        - days: `d`, `D`, `day`, `days`
        - hours: `H`, `h`, `hour`, `hours`
        - minutes: `M`, `minute`, `minutes`
        - seconds: `S`, `s`, `second`, `seconds`
        The units need to be provided in descending order of magnitude.
        """
        match = self.duration_parser.fullmatch(duration)
        if not match:
            raise BadArgument(f"`{duration}` is not a valid duration string.")

        duration_dict = {unit: int(amount) for unit, amount in match.groupdict(default=0).items()}
        delta = relativedelta(**duration_dict)
        now = datetime.now()

        try:
            return now + delta
        except ValueError:
            raise BadArgument(f"`{duration}` results in a datetime outside the supported range.")


class ISODateTime(Converter):
    """Converts an ISO-8601 datetime string into a datetime.datetime."""

    async def convert(self, ctx: Context, datetime_string: str) -> datetime:
        """
        Converts a ISO-8601 `datetime_string` into a `datetime.datetime` object.
        The converter is flexible in the formats it accepts, as it uses the `isoparse` method of
        `dateutil.parser`. In general, it accepts datetime strings that start with a date,
        optionally followed by a time. Specifying a timezone offset in the datetime string is
        supported, but the `datetime` object will be converted to UTC and will be returned without
        `tzinfo` as a timezone-unaware `datetime` object.
        See: https://dateutil.readthedocs.io/en/stable/parser.html#dateutil.parser.isoparse
        Formats that are guaranteed to be valid by our tests are:
        - `YYYY-mm-ddTHH:MM:SSZ` | `YYYY-mm-dd HH:MM:SSZ`
        - `YYYY-mm-ddTHH:MM:SS±HH:MM` | `YYYY-mm-dd HH:MM:SS±HH:MM`
        - `YYYY-mm-ddTHH:MM:SS±HHMM` | `YYYY-mm-dd HH:MM:SS±HHMM`
        - `YYYY-mm-ddTHH:MM:SS±HH` | `YYYY-mm-dd HH:MM:SS±HH`
        - `YYYY-mm-ddTHH:MM:SS` | `YYYY-mm-dd HH:MM:SS`
        - `YYYY-mm-ddTHH:MM` | `YYYY-mm-dd HH:MM`
        - `YYYY-mm-dd`
        - `YYYY-mm`
        - `YYYY`
        Note: ISO-8601 specifies a `T` as the separator between the date and the time part of the
        datetime string. The converter accepts both a `T` and a single space character.
        """
        try:
            dt = dateutil.parser.isoparse(datetime_string)
        except ValueError:
            raise BadArgument(f"`{datetime_string}` is not a valid ISO-8601 datetime string")

        if dt.tzinfo:
            dt = dt.replace(tzinfo=None)

        return dt


Expiry = Union[Duration, ISODateTime]
