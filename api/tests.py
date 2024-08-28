import unittest
import json
import uuid
from fastapi.testclient import TestClient
from main import app  # замените на ваш модуль, где инициализировано приложение FastAPI

client = TestClient(app)

class LogIn(unittest.TestCase):
    def test_wrong_code(self):
        response = client.get("/api/discord/auth?code=wrong_code")
        self.assertEqual(response.status_code, 401)

    def test_code(self):
        response = client.get(f"/api/discord/auth?code={input('code - >')}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.json()['response'])
        print("ACCESS_TOKEN = ", response.json()['response']['access_token'])


class OpenTicket(unittest.TestCase):
    token = '1sgWbOfUPXzDUDthUYG8SP5TFFR0lM'

    def test_open(self):
        response = client.get(
            "/api/tickets/open?text=Test ticket",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertIn("guid_ticket", response.json()['response'])

    def test_open_wrong_token(self):
        response = client.get(
            "/api/tickets/open?text=Test ticket",
            headers={"Authorization": "Bearer wrong_token"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 401)

    def test_open_without_text(self):
        response = client.get(
            "/api/tickets/open",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 422)


class ChangeState(unittest.TestCase):
    token = '1sgWbOfUPXzDUDthUYG8SP5TFFR0lM'
    guid_ticket = '7e80ec21-5742-4f9a-9d23-145922d32071'

    def test_change_state(self):
        response = client.get(
            f"/api/tickets/change_status?guid_ticket={self.guid_ticket}&new_status=processing",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 200)

    def test_change_state_same_state(self):
        response = client.get(
            f"/api/tickets/change_status?guid_ticket={self.guid_ticket}&new_status=processing",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 400)

    def test_change_state_wrong_token(self):
        response = client.get(
            f"/api/tickets/change_status?guid_ticket={self.guid_ticket}&new_status=processing",
            headers={"Authorization": "Bearer wrong_token"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 401)

    def test_change_state_without_new_status(self):
        response = client.get(
            f"/api/tickets/change_status?guid_ticket={self.guid_ticket}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 422)

    def test_change_state_without_guid_ticket(self):
        response = client.get(
            f"/api/tickets/change_status?new_status=processing",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 422)


class GetTickets(unittest.TestCase):
    token = '1sgWbOfUPXzDUDthUYG8SP5TFFR0lM'
    guid_ticket = '7e80ec21-5742-4f9a-9d23-145922d32071'
    not_guid_ticket = str(uuid.uuid4())
    author = '454570874410893322'

    def test_get_tickets(self):
        response = client.get(
            "/api/tickets/get",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()['response'].get('relevant_tickets', [])) > 0)

    def test_get_tickets_not_exists(self):
        response = client.get(
            f"/api/tickets/get?guid_ticket={self.not_guid_ticket}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['response'].get('relevant_tickets', []), [])

    def test_get_tickets_exists(self):
        response = client.get(
            f"/api/tickets/get?guid_ticket={self.guid_ticket}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()['response'].get('relevant_tickets', [])) == 1)

    def test_get_tickets_author(self):
        response = client.get(
            f"/api/tickets/get?author={self.author}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()['response'].get('relevant_tickets', [])) > 0)

    def test_get_tickets_wrong_author(self):
        response = client.get(
            "/api/tickets/get?author=wrong_author",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()['response'].get('relevant_tickets', [])) == 0, True)

    def test_get_tickets_status(self):
        response = client.get(
            "/api/tickets/get?status=open",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()['response'].get('relevant_tickets', [])) > 0)

    def test_get_tickets_wrong_status(self):
        response = client.get(
            "/api/tickets/get?status=wrong_status",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        print("response = ", response.json())
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
