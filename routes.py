import asyncio
import random

import asqlite
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route

import db

INVIS_CHARS = ("\u200d", "\u2060", "\u200b", "\u200c")
chars = "qwertyuiopasdfghjklzxcvbnm,1234567890QWERTYUIOPASDFGHJKKLZXCVBNM"


async def upload_endpoint(request: Request):
    form = await request.form()
    file = form.get("data")
    token = request.headers.get("token")
    e = None
    if not token:
        e = {"status_code": 400, "error": "no 'token' given"}
    elif not file:
        e = {"status_code": 400, "error": "no 'file' given"}
    elif token != request.app.token:
        e = {"status_code": 401, "error": "Invalid Authorization"}

    if e:
        return JSONResponse(e, status_code=e["status_code"])

    filename = "".join(random.choice(INVIS_CHARS) for _ in range(15))

    try:
        await file.seek(0)  # type: ignore
        image = await file.read()  # type: ignore
    except Exception as e:
        return JSONResponse(
            {"error": "Invalid 'file' given.", "status_code": 400},
            status_code=400,
        )

    mime = request.headers.get("mime") or file.content_type  # type: ignore
    if ";" in mime:
        mime = mime.split(";")[0]
    deletion_code = "".join(random.choice(chars) for i in range(15))
    print(f"{mime=}")
    await db.cache.add(
        _bytes=image, key=filename, mimetype=mime, delete_code=deletion_code
    )
    url = str(request.url).removesuffix("/upload")
    content = {
        "status_code": 200,
        "file_id": filename,
        "url": f"{url}/{filename}",
        "deletion_url": f"{url}/delete?code={deletion_code}",
        "deletion_code": deletion_code,
    }
    await db.logs.add("upload image", content["url"])
    return JSONResponse(content, status_code=200)


async def delete_endpoint(request: Request):
    code = request.query_params.get("code")

    if code is None:
        return HTMLResponse(
            "<h1>No Code Given</h1><br>401, No Code Given</br>", status_code=404
        )

    img = db.cache._internal_delete.get(code)

    if img is None:
        return HTMLResponse(
            "<h1>Image not found</h1><br>404, image not found</br>", status_code=404
        )

    async with asqlite.connect("data.db") as con:
        async with con.cursor() as cur:
            await cur.execute("DELETE FROM files WHERE delete_code = $1", (code))
            await con.commit()

    loop = asyncio.get_running_loop()
    loop.create_task(db.cache.fetch())
    return HTMLResponse("<h1>Done</h1>", status_code=404)


async def get_endpoint(request: Request):
    _id = request.path_params.get("id")

    img = db.cache[_id]
    if img is None:
        return HTMLResponse(
            "<h1>Image not found</h1><br>404, image not found</br>", status_code=404
        )

    return Response(img.bytes, media_type=img.mime, status_code=200)


ROUTES = [
    Route("/upload", upload_endpoint, methods=["POST"]),
    Route("/delete", delete_endpoint),
    Route("/{id}", get_endpoint),
]
