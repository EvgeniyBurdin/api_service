""" Запуск сервиса."""

from aiohttp import web

from middlewares.utils import ArgumentsManager
from middlewares.wrap_json import WrapExample
from settings import SERVICE_HOST, SERVICE_PORT
from urls import routes


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

    wrap_example = WrapExample(arguments_manager=arguments_manager)

    app.middlewares.append(wrap_example.middleware)

    return app


if __name__ == "__main__":

    app = get_app()

    web.run_app(app, host=SERVICE_HOST, port=SERVICE_PORT)
