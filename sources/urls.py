from aiohttp import web

from handlers import create, info, read


routes = [
    web.post("/create", create),
    web.get("/info/{info_id}", info),
    web.post("/read", read),
]
