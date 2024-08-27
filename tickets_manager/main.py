import asyncio
import datetime
import os
import uuid
from typing import Union

import requests
from requests import HTTPError
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker, Session

from cache import ActionsPool, ActionsLogs, NotificationsLogs, Action
from orm import DataClasses
TypeAction = DataClasses.TypeAction
DATABASE_URL = os.getenv("DATABASE_URL")


def response_format(func):
    def wrapped(*args, **kwargs) -> dict:
        r = func(*args, **kwargs)
        r.raise_for_status()
        data = r.json()
        return data

    return wrapped


def finish_task(session):
    def get_func(func):
        def wrapped(*args, **kwargs):
            data = dict(
                metadata=kwargs['request_data'],
                success=True,
                response=dict()
            )
            try:
                data['response'] = func(*args, **kwargs)
            except HTTPError as e:
                data['success'] = False
                data['response'] = dict(
                    code='UNAUTHORIZED',
                    request=e.request, args=e.args, response=e.response)
            except (TypeError, AssertionError) as e:
                data['success'] = False
                data['response'] = dict(
                    code='BAD_REQUEST',
                    description=e.args[0])
            except AttributeError as e:
                data['success'] = False
                data['response'] = dict(
                    code='UNAUTHORIZED',
                    response=e.args[1])
            finally:
                model = ActionsLogs.add(
                    guid=kwargs['guid_action'],
                    **data
                )
                assert model is None  # todo УБРАТЬ, а если появилось ошибка, то тут проблема!!!!!!!
            session.commit()

            return model.dict()

        return wrapped

    return get_func

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

    @staticmethod
    def get_idInDB(access_token: str, session: Session) -> Union[None, tuple]:
        user_data = Discord(access_token).get_me()
        id = session.query(DataClasses.User.id).filter_by(id=user_data['id']).first()
        return id

    @staticmethod
    def get_meInDB(access_token: str, session: Session) -> Union[None, DataClasses.User]:
        user_data = Discord(access_token).get_me()
        found_user = session.query(DataClasses.User).filter_by(id=user_data['id']).first()
        return found_user



class Reaction:
    # engine = create_async_engine(
    #     DATABASE_URL,
    #     echo=True,
    # )
    # async_session = async_sessionmaker(engine, expire_on_commit=False)
    # async with async_session() as session:
    engine = create_engine(DATABASE_URL)
    factory = sessionmaker(bind=engine)
    session = factory()

    @classmethod
    @finish_task(session)
    def log_in(cls, request_data):
        """
        Данный метод призван обработать авторизацию через систему Discord OAuth2.0
        :param request_data: коллекция с нужными параметрами для выполнения запроса.
            Обязательные ключи: code, guid_action
        :return: dict либо ошибку
        """

        token_data = Discord.exchange_code(request_data['code'])

        if "access_token" in token_data:
            user_data = Discord(token_data["access_token"]).get_me()
            existed_user = cls.session.query(DataClasses.User).filter_by(id=user_data['id']).first()
            if existed_user is not None:
                existed_user.access_token = token_data["access_token"]
                existed_user.dt_token_update = int(datetime.datetime.now().timestamp()),
                existed_user.expire_in = token_data['expires_in']
            else:
                cls.session.add(
                    DataClasses.User(
                        id=user_data['id'],
                        access_token=token_data['access_token'],
                        dt_token_update=int(datetime.datetime.now().timestamp()),
                        expire_in=token_data['expires_in'],
                        email=user_data['email']
                    )
                )

            return dict(
                author=user_data['id'],
                access_token=token_data['access_token'],
                dt_token_update=int(datetime.datetime.now().timestamp()),
                expire_in=token_data['expires_in'],
                email=user_data['email']
            )
        raise AttributeError(f"Something went wrong... Service did return not expected result", token_data)

    @classmethod
    @finish_task(session)
    def open_ticket(cls, request_data):
        """
        Данный метод призван обработать запрос на открытие заявки
        :param request_data: коллекция с нужными параметрами для выполнения запроса.
            Обязательные ключи: access_token, guid_action, guid_ticket
        :return: dict либо ошибку
        """
        user_id = Discord.get_idInDB(request_data['access_token'], session=cls.session)
        # todo заменить на декоратор общий, чтобы он обогощал requests_data 
        obj = dict(
            guid_ticket=request_data.get("guid_ticket", uuid.uuid4()),
            author=user_id,
            status=DataClasses.StatusTicket.open
        )
        cls.session.add(
            DataClasses.Tickets(**obj)
        )
        return obj

    @classmethod
    @finish_task(session)
    def error(cls, request_data):
        """
        Данный метод призван вызвать ошибку
        :param request_data: коллекция с нужными параметрами для выполнения запроса.
            Обязательные ключи: guid_action
        :return: ошибку
        """
        return AssertionError("WRONG TYPE ACTION")


    @classmethod
    @finish_task(session)
    def change_state(cls, request_data):
        """
        Данный метод призван обработать запрос на открытие заявки
        :param request_data: коллекция с нужными параметрами для выполнения запроса.
            Обязательные ключи: access_token, guid_action, guid_ticket, new_status
        :return: dict либо ошибку
        """
        user_id = Discord.get_idInDB(request_data['access_token'], session=cls.session)
        # todo заменить на декоратор общий, чтобы он обогощал requests_data
        if request_data['new_status'] in [action.value for action in DataClasses.StatusTicket]:
            obj = cls.session.query(DataClasses.Tickets).filter_by(guid_ticket=request_data['guid_ticket']).first()
            if obj is not None:
                old_status = str(obj.status)
                obj.status = request_data['new_status']
                return dict(
                    author=user_id,
                    old_status=old_status,
                    new_status=request_data['new_status']
                )

            raise TypeError("Ticket with entered guid_ticket does not exist!")
        raise TypeError("Status can't be entered because it's not in the list of allowed ticket statuses!")

router = {
        TypeAction.log_in: lambda: 'log_in', #Reaction.log_in,
        TypeAction.change_state: lambda: 'change_state', #Reaction.change_state,
        TypeAction.open_ticket: lambda: 'open_ticket', #Reaction.open_ticket,
    }
async def main():
    pool = ActionsPool()

    async def handler(task_dict):
        action = Action(**task_dict)
        try:
            func: Union[Reaction.log_in, Reaction.open_ticket, Reaction.change_state] = None
            for enum, func_handle in router.items():
                if enum.value == action.type.value:
                    func = func_handle
                    break

            if func is not None:
                request_data = dict(
                    **action.data,
                    guid_action=action.guid_action
                )
                return func(request_data)
        finally:
            return Reaction.error(dict(guid_action=action.guid_action))


    while True:
        tasks = pool.tasks()
        await asyncio.gather(*[handler(action_dict) for action_dict in tasks])


if __name__ == "__main__":
    asyncio.run(main())


