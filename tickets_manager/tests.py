import datetime
import os
import unittest
import uuid
import asyncio

from cache import Action, TypeAction, ActionsLogs, StatusTicket


class LogIn(unittest.TestCase):
    def test_wrong_code(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.log_in,
            data=dict(
                code='pkMGUsimCJvOnDDGdAcpl6jAIT3KIx'  # input(f"code({os.getenv('URL_AUTH')}) ->")
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        self.assertEqual(catcher.success, False)

    def test_code(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.log_in,
            data=dict(
                code=input(f"code({os.getenv('URL_AUTH')}) ->")
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)
        print("ACCESS_TOKEN = ", catcher.response['access_token'])


class open_ticket(unittest.TestCase):
    token = '1sgWbOfUPXzDUDthUYG8SP5TFFR0lM'

    def test_open(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.open_ticket,
            data=dict(
                access_token=self.token,
                text="Я доволен этой компанией!"
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)

    def test_open_wrong_token(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.open_ticket,
            data=dict(
                access_token=self.token+"1",
                text="Я доволен этой компанией!"
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, False)

    def test_open_without_text(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.open_ticket,
            data=dict(
                access_token=self.token,
                # text="Я доволен этой компанией!"
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)


class change_state(unittest.TestCase):
    token = '1sgWbOfUPXzDUDthUYG8SP5TFFR0lM'
    guid_ticket = 'd1102f20-382d-4693-9e63-f07a6d949244'

    def test_change_state(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.change_state,
            data=dict(
                access_token=self.token,
                guid_ticket=self.guid_ticket,
                new_status=StatusTicket.closed_fail
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)

    def test_change_state_same_state(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.change_state,
            data=dict(
                access_token=self.token,
                guid_ticket=self.guid_ticket,
                new_status=StatusTicket.closed_fail
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, False)

    def test_change_state_wrong_token(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.change_state,
            data=dict(
                access_token=self.token+"1",
                guid_ticket=self.guid_ticket,
                new_status=StatusTicket.closed_fail
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, False)

    def test_change_state_without_new_status(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.change_state,
            data=dict(
                access_token=self.token,
                guid_ticket=self.guid_ticket,
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, False)

    def test_change_state_without_new_status_guid_ticket(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.change_state,
            data=dict(
                access_token=self.token,
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, False)


class get_tickets(unittest.TestCase):
    token = '1sgWbOfUPXzDUDthUYG8SP5TFFR0lM'
    guid_ticket = 'a2e4e258-75c1-4a68-b50a-b6f7a04c3e3e'
    not_guid_ticket = str(uuid.uuid4())
    author = '454570874410893322'

    def test_get_tickets(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.get_tickets,
            data=dict(
                access_token=self.token,
                # guid_ticket=self.guid_ticket,
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)
        self.assertEqual(bool(len(catcher.response['relevant_tickets'])), True)

    def test_get_tickets_not_exists(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.get_tickets,
            data=dict(
                access_token=self.token,
                guid_ticket=self.not_guid_ticket,
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)
        self.assertEqual(catcher.response['relevant_tickets'], [])

    def test_get_tickets_exists(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.get_tickets,
            data=dict(
                access_token=self.token,
                guid_ticket=self.guid_ticket,
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)
        self.assertEqual(len(catcher.response['relevant_tickets']) == 1, True)

    def test_get_tickets_author(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.get_tickets,
            data=dict(
                access_token=self.token,
                author=self.author,
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)
        self.assertEqual(bool(len(catcher.response['relevant_tickets'])), True)

    def test_get_tickets_wrong_author(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.get_tickets,
            data=dict(
                access_token=self.token,
                author=self.author+"d",
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)
        self.assertEqual(len(catcher.response['relevant_tickets']) == 0, True)

    def test_get_tickets_status(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.get_tickets,
            data=dict(
                access_token=self.token,
                status=StatusTicket.closed_fail.value,
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, True)
        self.assertEqual(bool(len(catcher.response['relevant_tickets'])), True)

    def test_get_tickets_wrong_status(self):
        guid = str(uuid.uuid4())

        action_request = Action.create(
            _type=TypeAction.get_tickets,
            data=dict(
                access_token=self.token,
                status=StatusTicket.closed_fail.value+"d",
            ),
            guid_action=guid
        )
        catcher = asyncio.run(ActionsLogs.catch(guid, timeout=1))
        print("response = ", catcher.response)
        self.assertEqual(catcher.success, False)
        # self.assertEqual(len(catcher.response['relevant_tickets']) == 0, True)


if __name__ == '__main__':
    unittest.main()
