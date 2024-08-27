from datetime import datetime
from typing import List, Dict
from uuid import UUID

from pydantic import HttpUrl, Field, field_serializer
from schema_base import BaseModel_http


class AuthResponseGET(BaseModel_http):
    link: HttpUrl = Field(description="Ссылка для аутентификация через OAuth 2.0 от Discord")


class AuthResponsePOST(BaseModel_http):
    access_token: UUID = Field(description="Токен, при помощи которого можно осуществлять использование API сервиса заявок")
    expire_in: datetime = Field(description="Временная метка, до которой будет работать токен")

    @field_serializer('expire_in')
    def serialize_expire_in(self, expire_in: datetime, _info):
        return int(expire_in.timestamp())

    @field_serializer('access_token')
    def serialize_access_token(self, access_token, _info):
        return str(access_token)


class OpenTicket(BaseModel_http):
    guid_ticket: UUID = Field(description="Айди открытой заявки")

    @field_serializer('guid_ticket')
    def serialize_guid_ticket(self, guid_ticket, _info):
        return str(guid_ticket)

class ChangeState(BaseModel_http):
    timestamp_action: datetime = Field(description="Временная отметка завершения действия")
    previous_state: str = Field(description="Прошлый статус заявки")
    current_state: str = Field(description="Текущей изменнёный статус заявки")

class GetTicket(BaseModel_http):
    guid_ticket: UUID = Field(description="Айди заявки")
    dt_created: datetime = Field(description="Дата время создания заявки")
    author: int = Field(description="Айди пользователя, создавшего запрошенную заявка")
    current_state: str = Field(description="Текущий статус ошибки")
    history_actions: List[Dict] = Field(description="История изменений заявки")

    @field_serializer('dt_created')
    def serialize_dt_created(self, dt_created: datetime, _info):
        return int(dt_created.timestamp())

    @field_serializer('guid_ticket')
    def serialize_guid_ticket(self, guid_ticket, _info):
        return str(guid_ticket)

class SearchTickets(BaseModel_http):
    tickets: List[Dict] = Field(description="Список подходящих найденных заявок")
