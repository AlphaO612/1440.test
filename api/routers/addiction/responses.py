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


class