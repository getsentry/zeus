import asyncpg

from asyncpg import InterfaceError


class Database:
    def __init__(self, host: str, port: int, user: str, password: str, database: str):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

        self._conn = None

    async def connect(self):
        self._conn = await asyncpg.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            # we want to rely on pgbouncer
            statement_cache_size=0,
        )
        return self._conn

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def fetch(self, *args, **kwargs):
        if not self._conn:
            conn = await self.connect()
        else:
            conn = self._conn
        try:
            return await conn.fetch(*args, **kwargs)
        except InterfaceError as exc:
            if "connection is closed" in str(exc):
                conn = await self.connect()
                return await conn.fetch(*args, **kwargs)
            raise

    async def execute(self, *args, **kwargs):
        if not self._conn:
            conn = await self.connect()
        else:
            conn = self._conn
        try:
            return await conn.execute(*args, **kwargs)
        except InterfaceError as exc:
            if "connection is closed" in str(exc):
                conn = await self.connect()
                return await conn.execute(*args, **kwargs)
            raise

    async def transaction(self, *args, **kwargs):
        if not self._conn:
            conn = await self.connect()
        else:
            conn = self._conn
        try:
            return conn.transaction(*args, **kwargs)
        except InterfaceError as exc:
            if "connection is closed" in str(exc):
                conn = await self.connect()
                return conn.transaction(*args, **kwargs)
            raise
