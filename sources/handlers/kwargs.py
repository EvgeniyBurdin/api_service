""" Обработчики апи-методов.

    Обработчики могут иметь только такие аргументы:

    - request: web.Request - В него будет передаваться экземпляр web.Request
                            оригинального запроса.
                            Имя аргумента может быть любым (не обязательно
                            "request").
                            Аннотация обязательно должна быть типом
                            web.Request.

    - data: Any            - В него будут передаваться данные полученные из
                            json-тела запроса (в этом примере это то, что
                            отдаст используемая kwargs_handler.middleware).
                            Имя аргумента обязательно должно быть "data".
                            Аннотация может быть любой (нужно ставить ту,
                            которая описывает вх.данные для обработчика).

    - storage: dict        - В него будет передаваться передаваться
                            экземпляр хранилища .
                            Имя аргумента обязательно должно быть "storage".
                            Аннотация может быть любой (нужно ставить ту,
                            которая описывает экземпляр хранилища).

    - info_id: int          - В него будет передаваться значение полученное из
                            словаря request.match_info, то есть параметр
                            запроса из объявления url.
                            Имя аргумента обязательно должно быть "info_id".
                            Аннотация может быть любой (нужно ставить ту,
                            которая описывает вх.данные).
                            Использовать этот аргумент можно только в том
                            обрабочтике, для которого этот параметр описан
                            в url (иначе будет 500 ошибка KeyError).

    Внимание! Аннотации ко всем аргументам у обработчиков - обязательны!
"""
from typing import List, Union
from uuid import uuid4

from aiohttp import web


async def create(
    data: Union[dict, List[dict]], storage: dict,
) -> Union[dict, List[dict]]:
    """ Создает запись или несколько записей о персоне и сохраняет в хранилище.
        Возвращает созданную запись или их список.
    """
    data_is_list = isinstance(data, list)

    persons = data if data_is_list else [data, ]

    result = []
    for person in persons:
        person_info = dict(id=str(uuid4()), name=person["name"])

        # Добавим в хранилище новую запись
        storage[person_info["id"]] = person_info

        result.append(person_info)

    return result if data_is_list else result[0]


class PersonNotFound(Exception):
    pass


async def read(storage: dict, data: str) -> dict:
    """ Читает запись с id=data из хранилища, и возвращает её.
    """
    person = storage.get(data)

    if person is None:
        raise PersonNotFound(f"Person whith id={data} not found!")

    return dict(id=person["id"], name=person["name"])


async def info(info_id: int, request: web.Request) -> str:
    """ Информация.
    """
    return f"info_id={info_id} and request={request}"
