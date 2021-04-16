import pytest
from middlewares.exceptions import InputDataValidationError
from middlewares.simple_handler import SimpleHandler

simple_handler = SimpleHandler()


def test_get_error_body():
    """ Тело ответа с ошибкой
    """
    error_message = "Some error message"
    error = Exception(error_message)

    error_body = simple_handler.get_error_body(request={}, error=error)

    assert isinstance(error_body, dict)
    assert error_body["error_type"] == str(type(error))
    assert error_body["error_message"] == error_message


async def some_handler(_, request_body):
    return request_body


@pytest.mark.asyncio
async def test_is_json_service_handler_true():
    """ Хандлер действительно является одним из наших обработчиков
    """
    assert simple_handler.is_json_service_handler(
        request={}, handler=some_handler
    )


@pytest.mark.asyncio
async def test_is_json_service_handler_false():
    """ Хандлер НЕ является одним из наших обработчиков
    """
    # Передадим в handler любую "нефункцию"
    assert not simple_handler.is_json_service_handler(request={}, handler="")


@pytest.mark.asyncio
async def test_run_handler():
    """ Запуск хандлера и получение результата его работы
    """
    request_body = {"some_key": "some_value"}
    result = await simple_handler.run_handler({}, some_handler, request_body)
    assert result == request_body


@pytest.mark.asyncio
async def test_get_response_body_and_status_200():
    """ Получение результата работы хандлера и статуса 200
    """
    request_body = {"some_key": "some_value"}
    result = await simple_handler.get_response_body_and_status(
        request={}, handler=some_handler, request_body=request_body
    )
    assert result[1] == 200


@pytest.mark.asyncio
async def test_get_response_body_and_status_400():
    """ Получение результата ошибки хандлера и статуса 400
    """
    error_message = "Status 400"

    async def some_handler_400(_, request_body):
        raise InputDataValidationError(error_message)

    request_body = {"some_key": "some_value"}
    result = await simple_handler.get_response_body_and_status(
        request={}, handler=some_handler_400, request_body=request_body
    )
    assert error_message == result[0]["error_message"]
    assert "InputDataValidationError" in result[0]["error_type"]
    assert result[1] == 400


@pytest.mark.asyncio
async def test_get_response_body_and_status_500():
    """ Получение результата ошибки хандлера и статуса 500
    """
    error_message = "Status 500"

    async def some_handler_500(_, request_body):
        raise Exception(error_message)

    request_body = {"some_key": "some_value"}
    result = await simple_handler.get_response_body_and_status(
        request={}, handler=some_handler_500, request_body=request_body
    )
    assert error_message == result[0]["error_message"]
    assert "Exception" in result[0]["error_type"]
    assert result[1] == 500


@pytest.mark.asyncio
async def test_get_json_dumps():
    """ Получение строки json из объекта python
    """
    result = await simple_handler.get_json_dumps({}, {"foo": "bar"})
    assert result == '{"foo": "bar"}'


@pytest.mark.asyncio
async def test_response_text_and_status_200():
    """ Получение строки json из объекта python со статусом по умолчанию (200)
    """
    text, status = await simple_handler.get_response_text_and_status(
        {}, {"foo": "bar"}, 200
    )
    assert text == '{"foo": "bar"}'
    assert status == 200


@pytest.mark.asyncio
async def test_response_text_and_status_500():
    """ Получение строки json с описанием ошибки и статусом 500
    """
    not_json_serializable_object = complex(4, 3)

    text, status = await simple_handler.get_response_text_and_status(
        {}, not_json_serializable_object, 200
    )
    assert "TypeError" in text
    assert "is not JSON serializable" in text
    assert status == 500
