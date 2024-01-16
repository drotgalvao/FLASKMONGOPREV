import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, request
from user.user_controller import register_user, login_user, get_user
import bcrypt
from bson import ObjectId


class TestUserController(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.mongo = MagicMock()
        self.data = {
            "nome": "Test User",
            "email": "test@example.com",
            "password": "password",
        }
        self.hashed_password = bcrypt.hashpw(
            self.data["password"].encode("utf-8"), bcrypt.gensalt()
        )

    def test_register_user(self):
        self.mongo.db.users.find_one.return_value = None
        result = register_user(self.mongo, self.data)
        self.assertEqual(result[0]["message"], "User registered successfully")
        self.assertEqual(result[1], 201)

    def test_register_existing_user(self):
        self.mongo.db.users.find_one.return_value = True
        result = register_user(self.mongo, self.data)
        self.assertEqual(result[0]["error"], "Email already exists")
        self.assertEqual(result[1], 400)

    def test_login_user(self):
        with self.app.test_request_context(
            "/login", json={"email": "test@example.com", "password": "password"}
        ):
            self.mongo.db.users.find_one.return_value = {
                "_id": "some_id",
                "email": "test@example.com",
                "password": self.hashed_password.decode("utf-8"),
                "nome": "Test User",
            }
            result = login_user(self.mongo)
            self.assertIn("token", result.get_json())
            self.assertEqual(result.status_code, 200)



    def test_get_user(self):
        with self.app.app_context():
            user_id = str(ObjectId())
            expected_user = {
                "_id": user_id,
                "email": "test@example.com",
                "password": self.hashed_password.decode("utf-8"),
                "nome": "Test User",
            }
            self.mongo.db.users.find_one.return_value = expected_user

            result = get_user(self.mongo, user_id)

            data = result[0].get_json()

            self.assertEqual(data["_id"], user_id)
            self.assertEqual(result[1], 200)


if __name__ == "__main__":
    unittest.main()
