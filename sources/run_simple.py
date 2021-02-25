""" Запуск сервиса с простыми обработчиками.
"""
from aiohttp import web

from handlers.simple import handler500, some_handler
from middlewares.simple_handler import SimpleHandler
from settings import SERVICE_HOST, SERVICE_PORT

routes = [
    web.post("/some_handler", some_handler),
    web.post("/handler500", handler500),
]


def get_app() -> web.Application:

    app = web.Application()

    app.add_routes(routes)

    service_handler = SimpleHandler()

    app.middlewares.append(service_handler.middleware)

    return app


if __name__ == "__main__":

    app = get_app()

    web.run_app(app, host=SERVICE_HOST, port=SERVICE_PORT)
