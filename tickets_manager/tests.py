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
    guid_ticket = '414f9f30-9793-4d2d-96b9-277f1e4dc22b'

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


if __name__ == '__main__':
    unittest.main()
