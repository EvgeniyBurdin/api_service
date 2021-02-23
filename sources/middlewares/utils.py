import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Optional, Dict
from uuid import UUID


# json -----------------------------------------------------------------------

class ServiceJSONEncoder(json.JSONEncoder):
    """ Кодирование данных сервиса в json.

        (пример подключения обработки UUID и datetime)
    """
    def default(self, obj):

        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, datetime):
            return int(obj.timestamp())

        return json.JSONEncoder.default(self, obj)


def json_dumps(obj) -> str:
    """ Кодирования данных сервиса в json.
    """
    return json.dumps(obj, cls=ServiceJSONEncoder)


# ArgumentsManager -----------------------------------------------------------

@dataclass
class RawDataForArgument:

    request: Any
    request_body: Any
    arg_name: Optional[str] = None


class ArgumentsManager:
    """ Менеджер для аргументов обработчика.

        Связывает имя аргумента с действием, которое надо совершить для
        получения значения аргумента.
    """

    def __init__(self) -> None:

        self.getters: Dict[str, Callable] = {}

    # Тело json запроса ------------------------------------------------------

    def reg_request_body(self, arg_name) -> None:
        """ Регистрация имени аргумента для тела запроса.
        """
        self.getters[arg_name] = self.get_request_body

    def get_request_body(self, raw_data: RawDataForArgument) -> Callable:
        return raw_data.request_body

    # Ключи в request.app ----------------------------------------------------

    def reg_app_key(self, arg_name) -> None:
        """ Регистрация имени аргумента которых хранится в app.
        """
        self.getters[arg_name] = self.get_app_key

    def get_app_key(self, raw_data: RawDataForArgument):
        return raw_data.request.app[raw_data.arg_name]

    # Параметры запроса ------------------------------------------------------

    def reg_match_info_key(self, arg_name) -> None:
        """ Регистрация имени аргумента который приходит в параметрах запроса.
        """
        self.getters[arg_name] = self.get_match_info_key

    def get_match_info_key(self, raw_data: RawDataForArgument):
        return raw_data.request.match_info[raw_data.arg_name]

    # Можно добавить и другие регистраторы...
