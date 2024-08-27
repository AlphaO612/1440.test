from datetime import datetime
from uuid import uuid4, UUID
from enum import Enum
from typing import Union, Optional

from pydantic import BaseModel, field_serializer

from .pool import ActionsPool


class TypeAction(Enum):
    log_in = 'log_in'
    open_ticket = "open_ticket"
    change_state = "change_state"
    # error = 'error'

class StatusTicket(Enum):
    open = "open"
    processing = "processing"
    closed_success = "closed_success"
    closed_fail = "closed_fail"


class Action(BaseModel):
    type: TypeAction
    timestamp: datetime
    author: Optional[int]
    data: dict
    guid_action: Union[None, str, UUID]

    @field_serializer('timestamp')
    def serialize_timestamp(self, timestamp: datetime, _info):
        return int(timestamp.timestamp())

    @classmethod
    def create(cls,
               _type: TypeAction,
               data: dict,
               author: Optional[int] = None,
               guid_action: Union[None, str, UUID] = None
               ):
        if guid_action is None:
            guid_action = str(uuid4())

        obj = cls(
            guid_action=guid_action,
            timestamp=datetime.now(),
            type=_type,
            author=author,
            data=data
        )
        ActionsPool.add(obj)
        return obj
