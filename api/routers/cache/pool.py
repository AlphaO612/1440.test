import json

import redis
from pydantic import BaseModel

from . import settings

paths = settings.paths


class Pool:
    red = redis.StrictRedis(**settings.REDIS_AUTH)
    path: str = paths.queue.actions()

    def tasks(self) -> list[str]:
        item = self.red.brpop([self.path])[1::2]

        return list(map(lambda x: json.loads(x), item))

    @classmethod
    def add(cls, obj: BaseModel):
        cls.red.lpush(cls.path, obj.model_dump_json())


class ActionsPool(Pool):
    path = paths.queue.actions()


class NotificationsPool(Pool):
    path = paths.queue.notifications()
