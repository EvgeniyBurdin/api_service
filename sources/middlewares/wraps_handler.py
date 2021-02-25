from typing import Any, Callable

from aiohttp import web
from data_classes.wraps import WrapRequest, WrapResponse
from valdec.errors import ValidationArgumentsError

from middlewares.exceptions import InputDataValidationError
from middlewares.kwargs_handler import KwargsHandler

KEY_NAME_FOR_ID = "_wrap_request_value_id"


class WrapsKwargsHandler(KwargsHandler):
    """ Пример класса для middleware json-обработчиков api-методов которые
        имеют оболочки для запроса и ответа и валидацию.
    """

    def get_error_body(self, request: web.Request, error: Exception) -> dict:
        """ Формирует и отдает словарь с телом ответа с ошибкой.

            Для поля оболочки id использует сохраненное в request значение.
        """
        result = dict(error_type=str(type(error)), error_message=str(error))
        # Так как мы знаем какая у нас оболочка ответа, сразу сделаем словарь
        # с аналогичной "схемой"
        response = dict(
            success=False, result=result, id=request.get(KEY_NAME_FOR_ID)
        )
        return response

    async def run_handler(
        self, request: web.Request, handler: Callable, request_body: Any
    ) -> dict:

        id_ = None

        try:
            # Проведем валидацию оболочки запроса
            wrap_request = WrapRequest(**request_body)

        except Exception as error:
            message = f"{type(error).__name__} - {error}"
            raise InputDataValidationError(message)

        # Запомним поле id для ответов (сохранение id в словаре request
        # необходимо для использования значения id в ответе с ошибкой)
        id_ = wrap_request.id
        request[KEY_NAME_FOR_ID] = id_

        try:
            result = await super().run_handler(
                request, handler, wrap_request.data
            )
        except ValidationArgumentsError as error:
            message = f"{type(error).__name__} - {error}"
            raise InputDataValidationError(message)

        # Проведем валидацию оболочки ответа
        wrap_response = WrapResponse(success=True, result=result, id=id_)

        return wrap_response.dict()
