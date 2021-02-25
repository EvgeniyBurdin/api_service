""" Обработчики апи-методов.
"""
from aiohttp import web


async def some_handler(request: web.Request, data: dict) -> dict:
    """ Пример обработчика с простой сигнатурой.
    """
    return data


async def handler500(request: web.Request, data: dict) -> dict:
    """ Пример обработчика в котором произойдет ошибка.
    """
    raise Exception("Пример ошибки 500")

    return data
