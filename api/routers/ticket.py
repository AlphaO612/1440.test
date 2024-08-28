import datetime
import os, requests
import uuid
from typing import Optional

from fastapi import FastAPI, APIRouter, Query, HTTPException, Request
from pydantic import BaseModel
from http import HTTPStatus

from .addiction import Responses, Errors
from .addiction import ResPattern, ErrorAnswer
from .addiction.schema_base import JsonFormat_code
from .cache import Action, TypeAction, ActionsLogs
from .verify import verify_token, create_response, responses

URL_AUTH = os.getenv("URL_AUTH")
router = APIRouter()

API_ENDPOINT = 'https://discord.com/api/v10'
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = 'http://1440.arefaste.ru/'


@router.get("/open", status_code=200,
            summary="Метод для Открытия заявки пользователя",
            description="""**Нужен обязательно `access_token` в Headers['Authorization'] = 'Bearer <access_token>'**
            
            Метод используется для открытия заявки с текстом причины открытия и при успешности запроса получает `guid_ticket`
            """,
            responses={
                200: {"description": "Успешное получение 'guid_ticket'"},
                **responses
            })
@JsonFormat_code
async def open_ticket(req: Request,
                      text: str = Query(
                          description="Текст открываемой заявки"
                      )):
    success, response = await create_response(
        _type=TypeAction.open_ticket,
        data=dict(
            access_token=req.headers.get('Authorization', '').replace("Bearer ", "", 1),
            text=text
        )
    )
    if success:
        response = Responses.OpenTicket(
            guid_ticket=response['guid_ticket']
        )

    return ResPattern(
        success=response.status_code == HTTPStatus.OK,
        response=response.dict()
    )


@router.get("/change_status", status_code=200,
            summary="Метод для изменения статуса заявки",
            description="""**Нужен обязательно `access_token` в Headers['Authorization'] = 'Bearer <access_token>'**
            
            Метод используется для смены статуса существующей заявки и при успешности запроса получает `previous_status`
             и `current_status`
            # Входные параметры
              - guid_ticket = айди заявки, у которой нужно поменять статус
              - new_status = новый статус заявки из разрешённых('open', 'processing', 'closed_success', 'closed_fail')
            """,
            responses={
                200: {"description": "Успешное получение `previous_status` и `current_status`"},
                **responses
            })
@JsonFormat_code
async def change_status(req: Request,
                      guid_ticket: str = Query(
                          description="Айди заявки для смены статуса"
                      ),
                      new_status: str = Query(
                          description="Новый статус заявки",
                          examples=['open', 'processing', 'closed_success', 'closed_fail']
                      )):
    success, response = await create_response(
        _type=TypeAction.change_state,
        data=dict(
            access_token=req.headers.get('Authorization', '').replace("Bearer ", "", 1),
            guid_ticket=guid_ticket,
            new_status=new_status
        )
    )
    if success:
        response = Responses.ChangeState(
            previous_status=response['old_status'],
            current_status=response['new_status']
        )

    return ResPattern(
        success=response.status_code == HTTPStatus.OK,
        response=response.dict()
    )


@router.get("/get", status_code=200,
            summary="Метод для получения списка заявок",
            description="""**Нужен обязательно `access_token` в Headers['Authorization'] = 'Bearer <access_token>'**
            
            Метод используется для получения списка заявок с возможностью предварительной фильтрации и при успешности 
            запроса получает `relevant_tickets`
            # Входные параметры(фильтры)
            Тут все параметры являются не обязательными, поэтому для получения всего списка заявок, просто не указывайте
             параметры!
              - guid_ticket = айди заявки
              - author = создатель заявки
              - status = статус заявки из разрешённых('open', 'processing', 'closed_success', 'closed_fail')
            """,
            responses={
                200: {"description": "Успешное получение 'guid_ticket'"},
                **responses
            })
@JsonFormat_code
async def get_tickets(req: Request,
                      guid_ticket: Optional[str] = Query(
                          None,
                          description="Айди заявки"
                      ),
                      author: str = Query(
                          None,
                          description="Создатель заявки",
                          examples=['open', 'processing', 'closed_success', 'closed_fail']
                      ),
                      status: str = Query(
                          None,
                          description="Нынешний статус заявки"
                      )):
    success, response = await create_response(
        _type=TypeAction.get_tickets,
        data=dict(
            access_token=req.headers.get('Authorization', '').replace("Bearer ", "", 1),
            guid_ticket=guid_ticket,
            author=author,
            status=status
        )
    )
    if success:
        response = Responses.SearchTickets(
            relevant_tickets=response['relevant_tickets']
        )

    return ResPattern(
        success=response.status_code == HTTPStatus.OK,
        response=response.dict()
    )
