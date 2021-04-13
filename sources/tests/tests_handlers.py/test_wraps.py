from uuid import UUID, uuid4

import pytest
from aiohttp import web
from data_classes.person import PersonInfo
from handlers.wraps import PersonNotFound, create, info, read
from valdec.errors import ValidationArgumentsError


one_dict_for_create = {"name": "Ivan"}
create_params_names = "data, storage, result_type"
create_params_values = [
    # Если пришел словарь - на выходе PersonInfo, если список - то список
    (one_dict_for_create, {}, PersonInfo), ([one_dict_for_create, ], {}, list)
]


@pytest.mark.parametrize(create_params_names, create_params_values)
@pytest.mark.asyncio
async def test_create_result_type(data, storage, result_type):
    """ Если пришел словарь - на выходе PersonInfo, если список - то список
    """
    result = await create(data=data, storage=storage)

    assert isinstance(result, result_type)


@pytest.mark.asyncio
async def test_create():
    """ Создание записи о персоне
    """
    storage = {}

    result = await create(data=one_dict_for_create, storage=storage)

    assert isinstance(result.id, UUID)
    assert result.name == one_dict_for_create["name"]

    assert result.id in storage


@pytest.mark.asyncio
async def test_create_args_validation_errors():
    """ Ошибки валидации аргументов
    """
    with pytest.raises(ValidationArgumentsError):
        await create(data={"wrong_arg_name": "foo"}, storage={})

    with pytest.raises(ValidationArgumentsError):
        await create(data={"name": 1111111}, storage={})

    with pytest.raises(ValidationArgumentsError):
        await create(data=[{"name": 1111111}, {"name": 2222222}], storage={})


@pytest.mark.asyncio
async def test_read_successful():
    """ Успешное чтение записи о персоне
    """
    storage = {}

    create_result = await create(data=one_dict_for_create, storage=storage)

    person_id = create_result.id

    result = await read(data=person_id, storage=storage, req={})

    assert result.id == person_id
    assert result.name == one_dict_for_create["name"]


@pytest.mark.asyncio
async def test_read_args_validation_errors():
    """ Ошибки валидации аргумента
    """
    with pytest.raises(ValidationArgumentsError):
        await read(data="wrong_uuid", storage={}, req={})


@pytest.mark.asyncio
async def test_read_not_found_exception():
    """ Запись о персоне не найдена
    """
    some_wrong_id = uuid4()
    with pytest.raises(PersonNotFound):
        await read(data=some_wrong_id, storage={}, req={})


@pytest.mark.asyncio
async def test_info():
    """ Наличие web.Request в сигнатуре метода
    """
    annotations = list(info.__annotations__.values())

    assert web.Request in annotations


@pytest.mark.asyncio
async def test_info_args_validation_errors():
    """ Ошибки валидации аргумента
    """
    with pytest.raises(ValidationArgumentsError):
        await info(info_id="wrong_int", request={})
