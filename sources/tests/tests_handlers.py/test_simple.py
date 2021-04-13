import pytest
from aiohttp import web
from handlers.simple import handler500, some_handler


@pytest.mark.parametrize("handler", [some_handler, handler500])
def test_handler_signature(handler):
    """ Наличие web.Request и dict в сигнатуре метода, на первой и второй
        позиции, соответственно
    """
    # Возвращаем всегда словарь
    assert handler.__annotations__["return"] is dict

    args_annotations = list(handler.__annotations__.values())[:2]

    # Позиционные аргументы
    assert web.Request is args_annotations[0]
    assert dict is args_annotations[1]


@pytest.mark.asyncio
async def test_handler500_exception():
    """ Тест эмуляции исключения в методе handler500
    """
    with pytest.raises(Exception):
        await handler500({}, {})
