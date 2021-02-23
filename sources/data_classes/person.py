from uuid import UUID

from pydantic import Field, StrictStr

from data_classes.base import BaseApi


class PersonCreate(BaseApi):
    """ Парметры для создания персоны.
    """
    name: StrictStr = Field(description="Имя.", example="Oleg")


class PersonInfo(BaseApi):
    """ Информация о персоне.
    """
    id: UUID = Field(description="Идентификатор.")
    name: StrictStr = Field(description="Имя.")
