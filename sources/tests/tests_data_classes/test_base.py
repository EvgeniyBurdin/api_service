from data_classes.base import BaseApi
from pydantic import BaseModel, Extra


def test_subclass_pydantic_basemodel():
    """ BaseApi является наследником BaseModel
    """
    assert issubclass(BaseApi, BaseModel)


def test_base_api_extra_forbid():
    """ BaseApi не допускает дополнительные параметры при создании экземпляра
    """
    assert BaseApi.Config.extra == Extra.forbid
