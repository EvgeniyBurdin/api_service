""" Классы данных оболочек запроса и ответа.
"""
from typing import Any, Optional

from pydantic import Field, StrictInt

from data_classes.base import BaseApi

_ID_DESCRIPTION = "Идентификатор запроса к сервису."


class WrapRequest(BaseApi):
    """ Запрос.
    """
    data: Any = Field(description="Параметры запроса.", default=None)
    id: Optional[StrictInt] = Field(description=_ID_DESCRIPTION)


class WrapResponse(BaseApi):
    """ Ответ.
    """
    success: bool = Field(description="Статус ответа.", default=True)
    result: Any = Field(description="Результат ответа.")
    id: Optional[StrictInt] = Field(description=_ID_DESCRIPTION)
