from pydantic import BaseModel, Field, StrictStr


class ErrorResponse(BaseModel):
    """ Ответ с ошибкой.
    """
    error_type: StrictStr = Field(description="Наименование типа ошибки.")
    error_message: StrictStr = Field(description="Сообщение об ошибке.")
