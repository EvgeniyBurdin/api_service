import pytest
from aiohttp.web import Request
from middlewares.kwargs_handler import InvalidHandlerArgument, KwargsHandler
from middlewares.utils import ArgumentsManager


arguments_manager = ArgumentsManager()
arguments_manager.reg_request_key("some_arg_name")
kwargs_handler = KwargsHandler(arguments_manager=arguments_manager)


async def some_handler(some_arg_name: int):
    return some_arg_name + 111


def test_make_handler_kwargs():
    """ Формирование словаря с аргументами и их значениями для вызова метода
    """
    kwargs = {"some_arg_name": 1}

    result = kwargs_handler.make_handler_kwargs(
        request=kwargs,  # request используется как словарь, поэтому просто
                         # сунем в него словарь
        handler=some_handler, request_body={}
    )
    assert result == kwargs


@pytest.mark.asyncio
async def test_run_handler():
    """ Вызов обработчика и проверка результата его работы
    """
    kwargs = {"some_arg_name": 1}
    result = await kwargs_handler.run_handler(
        request=kwargs,  # request используется как словарь, поэтому просто
                         # сунем в него словарь
        handler=some_handler, request_body={}
    )
    assert result == kwargs["some_arg_name"] + 111


async def some_handler_with_request(some_arg_name: int, req: Request):
    return ""


def test_make_handler_kwargs_with_request():
    """ Формирование словаря с аргументами и их значениями для вызова метода
        (если в сигнатуре есть аргумент с аннотацией  Request)
    """
    data = {"some_arg_name": 1}

    result = kwargs_handler.make_handler_kwargs(
        request=data,  # request используется как словарь, поэтому просто
                       # сунем в него словарь
        handler=some_handler_with_request, request_body={}
    )
    assert "some_arg_name" in result
    assert result["some_arg_name"] == 1

    assert "req" in result
    assert result["req"] == data


async def wrong_handler(unregistered_argument_name: int):
    return ""


def test_make_handler_kwargs_fail():
    """ Исключение, если в сигнатуре обработчики есть незарегистрированный
        аргумент.
    """
    with pytest.raises(InvalidHandlerArgument) as error:
        kwargs_handler.make_handler_kwargs(
            request={}, handler=wrong_handler, request_body={}
        )
        assert str(wrong_handler) in error
        assert "unregistered_argument_name" in error
        assert str(str) in error


def test_build_error_message_for_invalid_handler_argument():
    """ Сообщение об ошибке содержит все необходимые сведения
    """
    result = kwargs_handler.build_error_message_for_invalid_handler_argument(
        wrong_handler, "unregistered_argument_name", str
    )
    assert str(wrong_handler) in result
    assert "unregistered_argument_name" in result
    assert str(str) in result
