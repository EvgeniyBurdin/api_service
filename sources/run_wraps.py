""" Запуск сервиса с обработчиками у которых именованные аргументы, оболочки
    запросов и валидация.
"""
from aiohttp import web

from handlers.wraps import create, info, read
from middlewares.utils import ArgumentsManager
from middlewares.wraps_handler import WrapsKwargsHandler
from settings import SERVICE_HOST, SERVICE_PORT

routes = [
    web.post("/create", create),
    web.get("/info/{info_id}", info),
    web.post("/read", read),
]


def get_app() -> web.Application:

    app = web.Application()

    app.add_routes(routes)

    arguments_manager = ArgumentsManager()

    # Регистрация имени аргумента обработчика, в который будут передаваться
    # данные полученные из json-тела запроса
    arguments_manager.reg_request_body("data")

    # В приложении будем использовать хранилище (это может, например, быть БД).
    # В текущем примере это просто словарь.
    app["storage"] = {}
    # Регистрация имени аргумента обработчика, в который будет передаваться
    # экземпляр хранилища
    arguments_manager.reg_app_key("storage")

    # Регистрация имени аргумента обработчика, в который будет передаваться
    # параметр запроса из словаря request.match_info
    arguments_manager.reg_match_info_key("info_id")

    service_handler = WrapsKwargsHandler(arguments_manager=arguments_manager)

    app.middlewares.append(service_handler.middleware)

    return app


if __name__ == "__main__":

    app = get_app()

    web.run_app(app, host=SERVICE_HOST, port=SERVICE_PORT)
