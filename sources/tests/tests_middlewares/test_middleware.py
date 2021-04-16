""" Тесты для middleware.
    Выполняем при помощи тестового клиенда aiohttp_client из pytest-aiohttp.
"""
from run_simple import get_app


async def test_middleware_200(aiohttp_client):
    """ Успешный ответ
    """
    app = get_app()
    client = await aiohttp_client(app)
    request_json = {"any": "json"}

    response = await client.post("/some_handler", json=request_json)
    response_json = await response.json()

    assert response.status == 200
    assert response_json == request_json


async def test_middleware_400(aiohttp_client):
    """ Ответ при ошибке в запросе
       (не передаем данные в post-запросе, поэтому получается ошибка 400)
    """
    app = get_app()
    client = await aiohttp_client(app)

    response = await client.post("/some_handler")

    assert response.status == 400


async def test_middleware_500(aiohttp_client):
    """ Ответ если произошла внутренняя ошибка сервиса
       (вызываем апи-метод handler500, который эмулирует ошибку сервиса)
    """
    app = get_app()
    client = await aiohttp_client(app)
    request_json = "any json"

    response = await client.post("/handler500", json=request_json)

    assert response.status == 500
