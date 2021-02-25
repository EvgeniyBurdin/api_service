""" Базовый класс данных для api.
"""
from pydantic import BaseModel, Extra


class BaseApi(BaseModel):
    """ Базовый класс данных для api.
    """
    class Config:
        # Следует ли игнорировать (ignore), разрешать (allow) или
        # запрещать (forbid) дополнительные атрибуты во время инициализации
        # модели, подробнее:
        # https://pydantic-docs.helpmanual.io/usage/model_config/
        extra = Extra.forbid
