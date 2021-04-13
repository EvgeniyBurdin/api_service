import pytest
from aiohttp import web
from handlers.kwargs import PersonNotFound, create, info, read


@pytest.mark.asyncio
async def test_create():
    """ Создание записи о персоне
    """
    data = {"name": "Ivan"}
    storage = {}

    result = await create(data=data, storage=storage)

    assert isinstance(result["id"], str)
    assert result["name"] == data["name"]

    assert result["id"] in storage


@pytest.mark.asyncio
async def test_read_successful():
    """ Успешное чтение записи о персоне
    """
    data = {"name": "Ivan"}
    storage = {}

    create_result = await create(data=data, storage=storage)

    person_id = create_result["id"]

    result = await read(data=person_id, storage=storage)

    assert result["id"] == person_id
    assert result["name"] == data["name"]


@pytest.mark.asyncio
async def test_read_not_found_exception():
    """ Запись о персоне не найдена
    """
    with pytest.raises(PersonNotFound):
        await read(data="some wrong id", storage={})


@pytest.mark.asyncio
async def test_info():
    """ Наличие web.Request в сигнатуре метода
    """
    annotations = list(info.__annotations__.values())

    assert web.Request in annotations
