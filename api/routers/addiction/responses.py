import datetime
from http import HTTPStatus
from typing import List, Dict
from uuid import UUID

from pydantic import HttpUrl, Field, field_serializer, BaseModel


class AuthResponseGET(BaseModel):
    status_code: int = Field(default=HTTPStatus.OK.value, description="статус запроса")
    link: str = Field(description="Ссылка для аутентификация через OAuth 2.0 от Discord")


class AuthResponsePOST(BaseModel):
    status_code: int = Field(default=HTTPStatus.OK.value, description="статус запроса")
    access_token: str = Field(description="Токен, при помощи которого можно осуществлять использование API сервиса заявок")
    expire_in: datetime.timedelta = Field(description="Временная метка, до которой будет работать токен")

    @field_serializer('expire_in')
    def serialize_expire_in(self, expire_in: datetime.timedelta, _info):
        return int(expire_in.total_seconds())

    @field_serializer('access_token')
    def serialize_access_token(self, access_token, _info):
        return str(access_token)


class OpenTicket(BaseModel):
    status_code: int = Field(default=HTTPStatus.OK.value, description="статус запроса")
    guid_ticket: UUID = Field(description="Айди открытой заявки")

    @field_serializer('guid_ticket')
    def serialize_guid_ticket(self, guid_ticket, _info):
        return str(guid_ticket)

class ChangeState(BaseModel):
    status_code: int = Field(default=HTTPStatus.OK.value, description="статус запроса")
    previous_status: str = Field(description="Прошлый статус заявки")
    current_status: str = Field(description="Текущей изменнёный статус заявки")

class SearchTickets(BaseModel):
    status_code: int = Field(default=HTTPStatus.OK.value, description="статус запроса")
    relevant_tickets: List[Dict] = Field(description="Список подходящих найденных заявок")

