from pathlib import Path
from typing import Optional

import aiohttp
# import apraw
import asyncpg
from discord.ext import commands

import scott_bot.util.constants
from .util.constants import DataBase


class ScottBot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)

        self.http_session: Optional[aiohttp.ClientSession] = None
        self.db_conn: Optional[asyncpg.Connection] = None
        self.reddit: Optional[scott_bot.util.constants.Reddit] = None

        self.loop.create_task(self.load_all_extensions())

    async def on_ready(self):
        print('Logged in as:')
        print(self.user)
        print(self.user.id)
        print('-' * len(str(self.user.id)))

    async def load_all_extensions(self):
        await self.wait_until_ready()
        p = Path.cwd() / 'scott_bot' / 'cogs'
        cogs = [x.stem for x in p.glob('*.py')]
        if "other_cog" in cogs:
            cogs.remove("other_cog")
            cogs.append("other_cog")
        extension = None
        for extension in cogs:
            self.load_extension(f'scott_bot.cogs.{extension}')
            print(f'loaded {extension}')

        print('-' * len(f'loaded {extension}'))

    async def login(self, token, *, bot=True):
        await self._recreate()
        await super().login(token, bot=bot)

    async def close(self):
        await super().close()
        await self._close()

    async def _create(self) -> None:
        self.http_session = aiohttp.ClientSession()
        self.db_conn = await asyncpg.create_pool(DataBase.db_url, password=DataBase.password)
        # self.reddit = apraw.Reddit(client_id=Reddit.client_id,
        #                            client_secret=Reddit.client_secret,
        #                            user_agent=Reddit.user_agent,
        #                            username=Reddit.username,
        #                            password=Reddit.password)

    async def _close(self) -> None:
        if self.http_session is not None:
            await self.http_session.close()

        if self.db_conn is not None:
            await self.db_conn.close()

    async def _recreate(self) -> None:
        await self._close()
        await self._create()
