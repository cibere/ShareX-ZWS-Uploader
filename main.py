import asqlite
from starlette.applications import Starlette

import db
from routes import ROUTES

app = Starlette(routes=ROUTES)

with open("secrets.txt") as f:
    tkn = f.read()
app.token = tkn  # type: ignore


@app.on_event("startup")
async def on_startup():
    async with asqlite.connect("data.db") as con:
        async with con.cursor() as cur:
            await cur.execute(
                "CREATE TABLE IF NOT EXISTS files (timestamp TEXT, key TEXT, file BYTES, mime TEXT, delete_code TEXT)"
            )
            await cur.execute(
                "CREATE TABLE IF NOT EXISTS logs (timestamp TEXT, action TEXT, link TEXT)"
            )
            await con.commit()
    await db.cache.fetch()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
