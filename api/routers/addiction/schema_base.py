from functools import wraps
from typing import Dict, Any, Union
from http import HTTPStatus
from pydantic import BaseModel, Field
from fastapi.responses import JSONResponse

from .responses import *

class BaseModel_http(BaseModel):
    status_code: int = Field(default=HTTPStatus.OK.value, description="статус запроса")

class ErrorAnswer(BaseModel):
    status_code: int = Field(description="Код http ответа(ошибки)")
    description: str = Field(description="Описание ошибки")


class Response(BaseModel):
    # metadata: Dict[str, Any] = Field(description="Вводные параметры")
    success: bool = Field(description="Успешно ли выполнен запрос или нет")
    response: Union[
        AuthResponseGET,
        AuthResponsePOST,
        OpenTicket,
        ChangeState,
        SearchTickets,
        ErrorAnswer
    ] = Field(description="Ответ на запрос")


def JsonFormat_code(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        res: Response = await func(*args, **kwargs)
        return JSONResponse(
            status_code=res.response.status_code,
            content=res.dict()
        )

    return wrapper