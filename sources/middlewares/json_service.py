""" Классы для middlewares."""

import types
from copy import copy
from typing import Any, Callable, Tuple

from aiohttp import web

from middlewares.errors_classes import (InputDataValidationError,
                                        InvalidHandlerArgument)
from middlewares.utils import ArgumentsManager, RawDataForArgument, json_dumps


class FullRequestAndJsonHandler:
    """ Класс для middleware json-обработчиков api-методов.

        Каждый обработчик должен иметь только два аргумента с произвольными
        именами:
        1. В первый будет отправлен оригинальный request.
        2. Во второй - результат request.json().
    """
    def get_error_body(self, request: web.Request, error: Exception) -> dict:
        """ Отдает словарь с телом ответа с ошибкой.

            (Этот метод надо переопределять, если нужен другой формат ответа)
        """
        return {"error_type": str(type(error)), "error_message": str(error)}

    def is_json_service_handler(
        self, request: web.Request, handler: Callable
    ) -> bool:
        """ Проверяет, является ли handler обработчиком сервиса.
        """
        # TODO Возможно, надо сделать надёжнее, или решить по другому
        return isinstance(handler, types.FunctionType)

    async def run_handler(
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> Any:
        """ Запускает реальный обработчик, и возвращает результат его работы.

            (Этот метод надо переопределять, если необходима дополнительная
            обработка запроса/ответа/исключений)
        """
        return await handler(request, request_body)

    async def get_response_body_and_status(
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> Tuple[Any, int]:
        """ Вызывает метод запуска обработчика и обрабатывает возможные
            ошибки.
            Возвращает объект с телом для ответа и код статуса ответа.
        """
        try:
            response_body = await self.run_handler(
                request, handler, request_body
            )
            status = 200

        except InputDataValidationError as error:
            response_body = self.get_error_body(request, error)
            status = 400

        except Exception as error:
            response_body = self.get_error_body(request, error)
            status = 500

        return response_body, status

    async def get_json_dumps(
        self, request: web.Request, response_body: Any
    ) -> str:
        """ Возвращает json-строку с дампом response_body.
        """
        return json_dumps(response_body)

    async def get_response_text_and_status(
        self, request: web.Request, response_body: Any, status: int
    ) -> Tuple[str, int]:
        """ Обрабатывает ошибку дампа объекта python в строку.
            Возвращает json-строку для ответа и код статуса ответа.
        """
        try:
            text = await self.get_json_dumps(request, response_body)

        except Exception as error:
            text = await self.get_json_dumps(
                self.get_error_body(request, error)
            )
            status = 500

        return text, status

    async def get_request_body(
        self, request: web.Request, handler: Callable
    ) -> Any:

        return await request.json()

    @web.middleware
    async def middleware(self, request: web.Request, handler: Callable):
        """ middleware для json-сервиса.
        """
        if not self.is_json_service_handler(request, handler):
            return await handler(request)

        try:
            request_body = await self.get_request_body(request, handler)

        except Exception as error:
            response_body = self.get_error_body(request, error)
            status = 400

        else:
            # Запуск обработчика
            response_body, status = await self.get_response_body_and_status(
                request, handler, request_body
            )

        finally:
            # Самостоятельно делаем дамп объекта python (который находится в
            # response_body) в строку json.
            text, status = await self.get_response_text_and_status(
                request, response_body, status
            )

        return web.Response(
            text=text, status=status,  content_type="application/json",
        )


class KwargsHandler(FullRequestAndJsonHandler):
    """ Класс добавляет для middleware возможность работать с обработчиками,
        которые могут иметь произвольное количество аргументов.

        Для этого каждый аргумент обработчика должен иметь аннотацию, и имя
        агрумента должно быть предварительно зарегистрировано при создании
        экземпляра web.Application().

        Все аргументы в обработчик передаются именованными, поэтому не важен
        порядок их определения в сигнатуре обработчика.

        Аргумент, который должен принять в обработчик оригинальный request,
        не требует регистрации. Он может иметь в сигнатуре обработчика любое
        имя, но у обязательно должен быть аннотирован типом: web.Request
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

            Внимание! Все аргументы у обработчиков иметь аннотации!
        """
        handler_kwargs = {}

        annotations = copy(handler.__annotations__)
        annotations.pop("return", None)

        raw_data = RawDataForArgument(request, request_body)

        for arg_name, annotation in annotations.items():

            # Если обработчик имеет аргумент с аннотацией aiohttp.web.Request,
            # то передадим в него экземпляр оригинального request
            if annotation is web.Request:
                handler_kwargs[arg_name] = request
                continue

            raw_data.arg_name = arg_name

            try:
                # get_arg_value - функция которая затем вернет нам значение для
                # аргумента с arg_name
                get_arg_value = self.arguments_manager.getters[arg_name]

            except KeyError:
                msg = self.build_error_message_for_invalid_handler_argument(
                    handler, arg_name, annotation
                )
                raise InvalidHandlerArgument(msg)

            handler_kwargs[arg_name] = get_arg_value(raw_data)

        return handler_kwargs

    async def run_handler(
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> Any:
        """ Запускает реальный обработчик, и возвращает результат его работы.

            (Этот метод надо переопределять, если необходима дополнительная
            обработка запроса/ответа/исключений)
        """
        handler_kwargs = self.make_handler_kwargs(
            request, handler, request_body
        )

        return await handler(**handler_kwargs)
