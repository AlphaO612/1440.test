import datetime
import json

import redis
import asyncio

from typing import Union
from uuid import UUID
from pydantic import BaseModel, Field

from . import settings

paths = settings.paths

_red = redis.StrictRedis(**settings.REDIS_AUTH)
class Logs(BaseModel):
    metadata: dict = Field(alias="metadata")
    success: bool = Field(alias="success")
    response: dict = Field(alias="response")
    _path = paths.logs.actions

    @classmethod
    def add(cls, guid: str, metadata: dict, success: bool, response: dict):
        obj = cls(metadata=metadata, success=success, response=response)
        # try:
        _red.set(cls._path(str(guid)), obj.model_dump_json())
        # except Exception as e:
        #     return None
        # finally:
        return obj

    @classmethod
    async def catch(cls, guid, timeout: int = 1):
        path = cls._path(str(guid))
        wait = await cls._wait(path, timeout)
        if wait is not None:
            return cls(**json.loads(wait))
        return None

    @classmethod
    async def _wait(cls, path: str, timeout: int):
        end_point = datetime.datetime.now() + datetime.timedelta(seconds=timeout)
        val = _red.get(path)
        while datetime.datetime.now() <= end_point and val is None:
            while val is None:
                await asyncio.sleep(0.3)
                val = _red.get(path)
        return val


class ActionsLogs(Logs):
    path = paths.logs.actions


class NotificationsLogs(Logs):
    path = paths.logs.notifications
