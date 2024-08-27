import asyncio
import datetime
import json
import os
import uuid
from typing import Union

from router import *

router = {
    TypeAction.log_in: Reaction.log_in,
    TypeAction.change_state: Reaction.change_state,
    TypeAction.open_ticket: Reaction.open_ticket,
}


async def main():
    pool = ActionsPool()

    async def handler(task_dict):
        action = Action(**task_dict)
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
            return func(request_data=request_data)
        else:
            return Reaction.error(request_data=dict(guid_action=action.guid_action))

    while True:
        print("started pooling...")
        tasks = pool.tasks()
        print("sending actions to the handler...")
        await asyncio.gather(*[handler(action_dict) for action_dict in tasks])


if __name__ == "__main__":
    asyncio.run(main())
