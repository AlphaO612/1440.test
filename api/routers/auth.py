import datetime
import os, requests
import uuid
from typing import Union

from fastapi import FastAPI, APIRouter, Query
from pydantic import BaseModel
from http import HTTPStatus

from .addiction import Responses, Errors
from .addiction import ResPattern, ErrorAnswer
from .addiction.schema_base import JsonFormat_code
from .cache import Action, TypeAction, ActionsLogs
from .verify import create_response, responses

URL_AUTH = os.getenv("URL_AUTH")
router = APIRouter()

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://1440.arefaste.ru/'


@router.get("/auth_link", status_code=200,
            summary="Метод для получения ссылки для авторизации",
            description="""Данная функция является начальной точкой при произведение авторизации.
            Тут получается ссылка для запроса прав у Discord OAuth2.0, а после получения кода он 
            должен передан методу /auth""",
            responses={
                200: {"description": "Успешное получения ссылки"}
            })
@JsonFormat_code
async def return_link():
    response = Responses.AuthResponseGET(
        link=URL_AUTH
    )

    return ResPattern(
        success=response.status_code == HTTPStatus.OK,
        response=response.dict()
    )


@router.get("/auth", status_code=200,
            summary="Метод для авторизации с помощью кода системы",
            description="""Данная функция является конечной точкой авторизации после /auth_link.""",
            responses={
                200: {"description": "Успешное получения токена"},
                **responses
            })
@JsonFormat_code
async def token_make(
        code: str = Query(
            description="Код для завершения авторизации через Discord OAuth2.0"
        )):
    success, response = await create_response(
        _type=TypeAction.log_in,
        data=dict(
            code=code
        )
    )
    if success:
        response = Responses.AuthResponsePOST(
            access_token=response['access_token'],
            expire_in=datetime.timedelta(seconds=response['expire_in'])
        )

    return ResPattern(
        success=response.status_code == HTTPStatus.OK,
        response=response.dict()
    )


