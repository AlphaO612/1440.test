from typing import Dict, Any, Union
from http import HTTPStatus
from pydantic import BaseModel, Field


class BaseModel_http(BaseModel):
    _status_code = HTTPStatus.OK
    @property
    def code(self):
        return self._status_code

class ErrorAnswer(BaseModel_http):
    status_code: HTTPStatus = Field(description="Код http ответа(ошибки)")
    description: str = Field(description="Описание ошибки")

    @property
    def code(self):
        return self.status_code


class Response(BaseModel):
    # metadata: Dict[str, Any] = Field(description="Вводные параметры")
    success: bool = Field(description="Успешно ли выполнен запрос или нет")
    response: Union[
        ErrorAnswer,
        AuthResponseGET,
        AuthResponsePOST,
        OpenTicket,
        ChangeState,
        GetTicket,
        SearchTickets
    ] = Field(description="Ответ на запрос")
