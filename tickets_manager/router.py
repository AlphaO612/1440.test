import datetime
import json
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
    def get_idInDB(access_token: str, session: Session, react_on_None: bool = True) -> Union[None, tuple]:
        user_data = Discord(access_token).get_me()
        id = session.query(DataClasses.User.id).filter_by(id=user_data['id']).first()
        if id is not None:
            id = id[0]
        else:
            if react_on_None:
                raise TypeError("Token not in db")
        return id

    @staticmethod
    def get_meInDB(access_token: str, session: Session) -> Union[None, DataClasses.User]:
        user_data = Discord(access_token).get_me()
        found_user = session.query(DataClasses.User).filter_by(id=user_data['id']).first()
        return found_user


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
                    request=dict(
                        url=str(e.request.url),
                        method=str(e.request.method),
                        headers=dict(e.request.headers),
                        body=str(e.request.body)
                    ), args=e.args, response=e.response.json())
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
            # except Exception as e:
            #     data['success'] = False
            #     data['response'] = dict(
            #         code='INTERNAL_ERROR',
            #         response=e.args[0])
            finally:
                data['metadata'].update(dict(
                    timestamp_action=int(datetime.datetime.now().timestamp())
                ))
                model = ActionsLogs.add(
                    guid=data['metadata']['guid_action'],
                    **data
                )
            session.commit()

            return model.dict()

        return wrapped

    return get_func


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
                existed_user.dt_token_update = datetime.datetime.now().timestamp(),
                existed_user.expire_in = datetime.timedelta(seconds=token_data['expires_in'])
            else:
                cls.session.add(
                    DataClasses.User(
                        id=user_data['id'],
                        access_token=token_data['access_token'],
                        dt_token_update=datetime.datetime.now(),
                        expire_in=datetime.timedelta(seconds=token_data['expires_in']),
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
            Обязательные ключи: access_token, guid_action, guid_ticket, text
        :return: dict либо ошибку
        """
        user_id = Discord.get_idInDB(request_data['access_token'], session=cls.session)
        # todo заменить на декоратор общий, чтобы он обогощал requests_data
        guid = request_data.get("guid_ticket", uuid.uuid4())
        obj = dict(
            guid_ticket=guid,
            author=user_id,
            status=DataClasses.StatusTicket.open
        )
        cls.session.add(
            DataClasses.Tickets(**obj)
        )

        cls.session.add(
            DataClasses.Actions(
                type=DataClasses.TypeAction.open_ticket,
                guid_ticket=guid,
                author=user_id,
                data=dict(
                    text=request_data.get("text")
                )
            )
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
        if 'guid_ticket' not in request_data:
            raise TypeError("guid_ticket not in data")
        if 'new_status' not in request_data:
            raise TypeError("guid_ticket not in data")
        if request_data['new_status'] in [action.value for action in DataClasses.StatusTicket]:
            obj = cls.session.query(DataClasses.Tickets).filter_by(guid_ticket=request_data['guid_ticket']).first()
            if obj is not None:
                if obj.status.value == request_data['new_status']:
                    raise TypeError("Same status!")

                old_status = obj.status.value
                obj.status = request_data['new_status']
                cls.session.add(
                    DataClasses.Actions(
                        type=TypeAction.change_state,
                        guid_ticket=request_data['guid_ticket'],
                        author=user_id,
                        data=dict(
                            old_status=old_status,
                            new_status=request_data['new_status']
                        )
                    )
                )
                return dict(
                    author=user_id,
                    old_status=old_status,
                    new_status=request_data['new_status']
                )

            raise TypeError("Ticket with entered guid_ticket does not exist!")
        raise TypeError("Status can't be entered because it's not in the list of allowed ticket statuses!")

    @classmethod
    @finish_task(session)
    def get_tickets(cls, request_data):
        """
        Данный метод призван возвращать данные о заявках с фильтрацией
        :param request_data: коллекция с нужными параметрами для выполнения запроса.
            Обязательные ключи: access_token, guid_action, guid_ticket, author, dt_created, status
        :return: dict либо ошибку
        """
        user_id = Discord.get_idInDB(request_data['access_token'], session=cls.session)
        # todo заменить на декоратор общий, чтобы он обогощал requests_data
        if request_data.get('status', None) is not None:
            if request_data['status'] not in [action.value for action in DataClasses.StatusTicket]:
                raise TypeError("Status must be in the list of allowed status")

        filter_dict = {}
        for key in ["guid_ticket", "author", "status"]:
            value = request_data.get(key, None)
            if value is not None:
                filter_dict[key] = value

        tickets_lst = cls.session.query(DataClasses.Tickets).filter_by(
            **filter_dict
        ).all()

        relevant_tickets = []
        for ticket in tickets_lst:
            a = dict(
                guid_ticket=ticket.guid_ticket,
                author=ticket.author,
                status=ticket.status,
                actions=[
                    dict(
                        author=action.author,
                        guid_ticket=str(action.guid_ticket),
                        timestamp=int(action.timestamp.timestamp()),
                        type=action.type.value,
                        data=action.data
                    )
                    for action in ticket.actions
                ]
            )
            relevant_tickets.append(a)
        return dict(relevant_tickets=relevant_tickets)
