import os
import uuid
from typing import Union

import requests
from fastapi import HTTPException, Request
from pydantic import BaseModel

from .addiction import Errors
from .cache import TypeAction, Action, ActionsLogs


def response_format(func):
    def wrapped(*args, **kwargs) -> dict:
        r = func(*args, **kwargs)
        # r.raise_for_status()
        data = r.json()
        return data

    return wrapped

class Discord:
    API_ENDPOINT = 'https://discord.com/api/v10'
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI")

    def __init__(self, access_token: str):
        self._token = access_token
        self.headers = {
            "Authorization": f"Bearer {self.token}"
        }

    @property
    def token(self):
        return self._token

    @response_format
    def get_me(self) -> dict:
        r = requests.get('%s/users/@me' % self.API_ENDPOINT, headers=self.headers)
        return r

    @classmethod
    @response_format
    def exchange_code(cls, code) -> dict:
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': cls.REDIRECT_URI
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        r = requests.post('%s/oauth2/token' % cls.API_ENDPOINT, data=data, headers=headers,
                          auth=(cls.CLIENT_ID, cls.CLIENT_SECRET))
        return r

responses = {
    401: {"description": "Ошибка о неправильной валидации кода(токена)"},
    500: {"description": "Внутренняя ошибка"},
    422: {"description": "Пропущен какой-то важный параметр при запросе"},
    400: {"description": "Ошибка в данных"},
}

def verify_token(req: Request):
    token = req.headers.get("Authorization", None)
    if token is None:
        raise HTTPException(
            status_code=401,
            detail="Wrong Token"
        )

    token = token.replace("Bearer ", "", 1)
    valid = Discord(token).get_me()
    if 'id' not in valid:
        raise HTTPException(
            status_code=401,
            detail="Wrong Token"
        )
    return True

async def create_response(_type: TypeAction, data: dict) -> tuple[bool, Union[BaseModel, dict]]:
    guid = str(uuid.uuid4())
    action_request = Action.create(
        _type=_type,
        data=data,
        guid_action=guid
    )
    catcher = await ActionsLogs.catch(guid, timeout=2)
    if catcher is not None:
        if catcher.success:
            return True, catcher.response
        else:
            error_pool = [
                             error.value
                             for error in Errors
                             if catcher.response['code'] == error.name
                         ] + [Errors.INTERNAL_ERROR.value]
            response = error_pool[0]
    else:
        response = Errors.INTERNAL_ERROR.value
    return False, response