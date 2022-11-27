import datetime
from typing import Optional

import asqlite


class Image:
    def __init__(self, *, _bytes, key, timestamp, mime, delete_code):
        self.bytes = _bytes
        self.key = key
        self.mime = mime
        self.ext = mime.split("/")[1]
        self.timestamp = timestamp
        self.delete_code = delete_code


class Cache:
    def __init__(self):
        self._internal_cache = {}
        self._internal_delete = {}

    def __getitem__(self, key) -> Image:
        item = self._internal_cache.get(key)
        return item  # type: ignore

    async def add(self, *, _bytes, key: str, mimetype: str, delete_code: str) -> Image:
        timestamp = str(datetime.datetime.utcnow())
        async with asqlite.connect("data.db") as con:
            async with con.cursor() as cur:
                await cur.execute(
                    "INSERT INTO files VALUES ($1, $2, $3, $4, $5)",
                    (timestamp, key, _bytes, mimetype, delete_code),
                )
                await con.commit()

        image = Image(
            _bytes=_bytes,
            key=key,
            timestamp=timestamp,
            mime=mimetype,
            delete_code=delete_code,
        )
        self._internal_cache[key] = image
        return image

    async def fetch(self) -> None:
        async with asqlite.connect("data.db") as con:
            async with con.cursor() as cur:
                await cur.execute("SELECT * FROM files")
                files = await cur.fetchall()

        cache = {}
        cache_to_del = {}
        for file in files:
            img = Image(
                _bytes=file[2],
                key=file[1],
                timestamp=file[0],
                mime=file[3],
                delete_code=file[4],
            )
            cache[img.key] = img
            cache_to_del[img.delete_code] = img

        self._internal_cache = cache
        self._internal_delete = cache_to_del


class Logs:
    def __init__(self):
        pass

    async def add(self, action: str, link: Optional[str] = None):
        timestamp = str(datetime.datetime.utcnow())

        async with asqlite.connect("data.db") as con:
            async with con.cursor() as cur:
                await cur.execute(
                    "INSERT INTO logs VALUES ($1, $2, $3)",
                    (timestamp, action, str(link)),
                )
                await con.commit()

    async def get_all(self):
        async with asqlite.connect("data.db") as con:
            async with con.cursor() as cur:
                await cur.execute("SELECT * FROM logs")
                data = await cur.fetchall()

        return list(data)


logs = Logs()
cache = Cache()
