import aiomysql
from aiomysql.connection import Connection
from aiomysql.cursors import DictCursor, Cursor

from asyncio.events import AbstractEventLoop, get_event_loop

from typing import Any


class MySQL:

    def __init__(
        self, 
        host: str, user: str,
        password: str, database: str,
        port: int = 3306,
        loop: AbstractEventLoop = None
        ):
        
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.loop = loop or get_event_loop()

    async def _connection(self) -> Connection:
        
        connect: Connection = await aiomysql.connect(
            host = self.host, user = self.user,
            password = self.password, 
            db = self.database, port = self.port,
            loop = self.loop
        )

        return connect

    def cursor(self, query: str, args: Any = None):
        
        self._query = query
        self._args = args

        return self

    async def commit(self):
        connect = await self._connection()
        async with connect.cursor(DictCursor) as cursor:
            cursor: Cursor 
            r = await cursor.execute(self._query, self._args)

        await connect.commit()
        connect.close()
        return r


    async def fetchone(self):
        connect = await self._connection()
        async with connect.cursor(DictCursor) as cursor:
            cursor: Cursor 
            await cursor.execute(self._query, self._args)
            response = await cursor.fetchone()

        connect.close()
        return response

    async def fetchall(self):
        connect = await self._connection()
        async with connect.cursor(DictCursor) as cursor:
            cursor: Cursor 
            await cursor.execute(self._query, self._args)
            response = await cursor.fetchall()

        connect.close()
        return response

    async def fetchmany(self, size: int = None):
        connect = await self._connection()
        async with connect.cursor(DictCursor) as cursor:
            cursor: Cursor 
            await cursor.execute(self._query, self._args)
            response = await cursor.fetchmany(size)

        connect.close()
        return response