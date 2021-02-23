""" Пример класса с middleware, которая реализует логику оболочек для
    запроса и ответа.
"""
from typing import Any, Callable

from aiohttp import web
from data_classes.errors import ErrorResponse
from data_classes.wraps import WrapRequest, WrapResponse
from valdec.errors import ValidationArgumentsError

from middlewares.errors_classes import InputDataValidationError
from middlewares.json_service import KwargsHandler


KEY_NAME_FOR_ID = "_wrap_request_value_id"


class WrapExample(KwargsHandler):
    """ Пример класса для middleware json-обработчиков api-методов которые
        имеют оболочки для запроса и ответа.

        Родительским классом можно выбрать и FullRequestAndJsonHandler,
        оболочка будет работать так же.
    """

    def get_error_body(self, request: web.Request, error: Exception) -> dict:

        result = ErrorResponse(
            error_type=str(type(error)), error_message=str(error)
        )
        response = WrapResponse(
            success=False,
            result=result,
            # Достанем id, если он был сохранен в методе run_handler()
            id=request.get(KEY_NAME_FOR_ID)
        )

        # Отдаем всегда словарь
        return response.dict()

    async def run_handler(
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> Any:

        id_ = None

        try:
            # Проведем валидацию оболочки запроса
            wrap_request = WrapRequest(**request_body)

            # Запомним поле id для ответов
            # (сохранение id в словаре request необходимо для использования
            # значения id в ответе с ошибкой)
            id_ = wrap_request.id
            request[KEY_NAME_FOR_ID] = id_

        except Exception as error:
            msg = f"{type(error).__name__} - {error}"
            raise InputDataValidationError(msg)

        try:
            result = await super().run_handler(
                request, handler, wrap_request.data
            )
        except ValidationArgumentsError as error:
            msg = f"{type(error).__name__} - {error}"
            raise InputDataValidationError(msg)

        # Проведем валидацию оболочки ответа
        wrap_response = WrapResponse(success=True, result=result, id=id_)

        # Отдаем всегда словарь
        return wrap_response.dict()
