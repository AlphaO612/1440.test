from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, HttpUrl, Field, field_serializer


class AuthResponseGET(BaseModel):
    link: HttpUrl = Field(description="Ссылка для аутентификация через OAuth 2.0 от Discord")


class AuthResponsePOST(BaseModel):
    access_token: UUID = Field(description="Токен, при помощи которого можно осуществлять использование API сервиса заявок")
    expire_in: datetime = Field(description="Временная метка, до которой будет работать токен")

    @field_serializer('expire_in')
    def serialize_expire_in(self, expire_in: datetime, _info):
        return expire_in.timestamp()

    @field_serializer('access_token')
    def serialize_access_token(self, access_token, _info):
        return str(access_token)


class OpenTicket(BaseModel):
    ticket_guid: UUID = Field(description="Айди открытой заявки")

    @field_serializer('ticket_guid')
    def serialize_ticket_guid(self, ticket_guid, _info):
        return str(ticket_guid)

class ChangeState(BaseModel):
    timestamp_action: datetime = Field(description="Временная отметка завершения действия")
    previus_state: str = Field(description="Прошлый статус заявки")
    current_state: str = Field(description="Текущей изменнёный статус заявки")

class GetTicket(BaseModel):
    ticket_guid: UUID = Field(description="Айди заявки")
    dt_created: datetime = Field(description="Дата время создания заявки")
    author: int = Field(description="Айди пользователя, создавшего запрошенную заявка")
    current_state: str = Field(description="Текущий статус ошибки")
    history_actions: List[Dict] = Field(description="История изменений заявки")

    @field_serializer('dt_created')
    def serialize_dt_created(self, dt_created: datetime, _info):
        return dt_created.timestamp()

    @field_serializer('ticket_guid')
    def serialize_ticket_guid(self, ticket_guid, _info):
        return str(ticket_guid)

class SearchTickets(BaseModel):
    tickets: List[Dict] = Field(description="Список подходящих найденных заявок")
