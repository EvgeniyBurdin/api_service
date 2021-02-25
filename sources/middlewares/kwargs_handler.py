from copy import copy
from typing import Any, Callable

from aiohttp import web

from middlewares.exceptions import InvalidHandlerArgument
from middlewares.simple_handler import SimpleHandler
from middlewares.utils import ArgumentsManager, RawDataForArgument


class KwargsHandler(SimpleHandler):
    """ Класс добавляет для middleware возможность работать с обработчиками,
        которые могут иметь произвольное количество аргументов.

        Для этого, каждый аргумент обработчика должен иметь аннотацию, и имя
        агрумента должно быть предварительно зарегистрировано при создании
        экземпляра web.Application().

        Все аргументы в обработчик передаются именованными, поэтому не важен
        порядок их определения в сигнатуре обработчика.

        Аргумент, который должен принять в обработчик оригинальный request,
        не требует регистрации. Он может иметь в сигнатуре обработчика любое
        имя, но обязательно должен быть аннотирован типом: web.Request
    """

    def __init__(self, arguments_manager: ArgumentsManager) -> None:

        self.arguments_manager = arguments_manager

    def build_error_message_for_invalid_handler_argument(
        self, handler: Callable, arg_name: str, annotation: Any
    ) -> str:
        """ Создает и возвращает строку и сообщеним об ошибке для исключения
            InvalidHandlerArgument.
        """
        message = f"KeyError - Invalid handler '{handler}' argument: "
        message += f"'{arg_name}': {annotation}'"

        return message

    def make_handler_kwargs(
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> dict:
        """ Собирает и возвращает kwargs для последующего его использования
            при вызове обработчика.

            Внимание! Все аргументы у обработчиков должны иметь аннотации.
        """
        kwargs = {}

        annotations = copy(handler.__annotations__)
        annotations.pop("return", None)

        raw_data = RawDataForArgument(request, request_body)

        for arg_name, annotation in annotations.items():

            # Если обработчик имеет аргумент с аннотацией aiohttp.web.Request,
            # то передадим в него экземпляр оригинального request
            if annotation is web.Request:
                kwargs[arg_name] = request
                continue

            raw_data.arg_name = arg_name

            try:
                # функция которая затем вернет нам значение для
                # аргумента с arg_name
                get_arg_value = self.arguments_manager.getters[arg_name]

            except KeyError:
                msg = self.build_error_message_for_invalid_handler_argument(
                    handler, arg_name, annotation
                )
                raise InvalidHandlerArgument(msg)

            kwargs[arg_name] = get_arg_value(raw_data)

        return kwargs

    async def run_handler(
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> Any:
        """ Запускает реальный обработчик, и возвращает результат его работы.

            (Этот метод надо переопределять, если необходима дополнительная
            обработка запроса/ответа/исключений)
        """
        kwargs = self.make_handler_kwargs(request, handler, request_body)

        return await handler(**kwargs)
