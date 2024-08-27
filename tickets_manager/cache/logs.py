import datetime
import json

import redis
import asyncio

from typing import Union
from uuid import UUID
from pydantic import BaseModel, Field

from . import settings

paths = settings.paths


class Logs(BaseModel):
    metadata: dict = Field(alias="metadata")
    success: bool = Field(alias="success")
    response: dict = Field(alias="response")

    _red = redis.StrictRedis(**settings.REDIS_AUTH)
    _path = paths.logs.actions

    @classmethod
    def add(cls, guid: str, metadata: dict, success: bool, response: dict):
        obj = cls(metadata=metadata, success=success, response=response)
        try:
            cls._red.set(cls._path(str(guid)), obj.model_dump_json())
        except Exception as e:
            return None
        finally:
            return obj

    @classmethod
    def catch(cls, guid, timeout: int = 1):
        path = cls._path(str(guid))
        if cls._wait(path, timeout):
            return cls(**json.loads(cls._red.get(path)))
        return None

    @classmethod
    def _wait(cls, path: str, timeout: int):
        end_point = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        while datetime.datetime.now() <= end_point:
            if cls._red.exists(path):
                return True
        return False


class ActionsLogs(Logs):
    path = paths.logs.actions


class NotificationsLogs(Logs):
    path = paths.logs.notifications
