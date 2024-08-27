import os

REDIS_AUTH = dict(
    host=os.getenv("HOST_REDIS"),
    port=6379,
    db=0,
    password=os.getenv("PWD_REDIS"),
)


class paths:
    class queue:
        actions = lambda: "queue:actions"
        notifications = lambda: "queue:notifications"

    class logs:
        actions = lambda guid_action: "logs:actions:{guid_action}".format(guid_action=guid_action)
        notifications = lambda guid_action: "logs:notifications:{guid_action}".format(guid_action=guid_action)

