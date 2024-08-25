from typing import Dict, Any, Union
from http import HTTPStatus
from pydantic import BaseModel, Field


class ErrorAnswer(BaseModel):
    status_code: HTTPStatus = Field(description="Код http ответа(ошибки)")
    description: str = Field(description="Описание ошибки")


class Response(BaseModel):
    # metadata: Dict[str, Any] = Field(description="Вводные параметры")
    success: bool = Field(description="Успешно ли выполнен запрос или нет")
    response: Union[ErrorAnswer, BaseModel] = Field(description="Ответ на запрос")

