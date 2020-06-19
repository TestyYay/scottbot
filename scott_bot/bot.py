from discord.ext import commands
import asyncio
import asyncpg
import aiohttp
from typing import Optional


class Bot(commands.Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self.http_session: Optional[aiohttp.ClientSession] = None
        self.db_conn: Optional[asyncpg.Connection] = None

    async def login(self, token, *, bot=True):
        await self._recreate()
        await super().login(token, bot=bot)

    async def close(self):
        await super().close()
        await self._close()

    async def _create(self) -> None:
        self.http_session = aiohttp.ClientSession()
        self.db_conn = await asyncpg.connect(self.conf.get('db_link'))

    async def _close(self) -> None:
        print("closing")
        if self.http_session:
            await self.http_session.close()

        if self.db_conn:
            await self.db_conn.close()

    async def _recreate(self) -> None:
        await self._close()
        await self._create()
