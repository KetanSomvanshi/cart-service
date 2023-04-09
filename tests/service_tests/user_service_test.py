import unittest
import uuid
from unittest.mock import patch, MagicMock

import http

from models.user import UserInsertModel, UserLoginModel, UserModel
from service.user_service import UserService
from utils.password_hasher import PasswordHasher


class TestUserService(unittest.TestCase):
    def setUp(self):
        self.user_insert_data = UserInsertModel(
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            role="customer",
            status="active",
            password="Password123@12"
        )
        self.user_login_data = UserLoginModel(
            email="johndoe@example.com",
            password="Password123@12"
        )
        self.user = UserModel(
            id=1,
            uuid=uuid.uuid4(),
            created_at="2023-04-09T14:53:10.285Z",
            is_deleted=False,
            first_name="John",
            last_name="Doe",
            email="johndoe@example.com",
            role="customer",
            status="active",
            password_hash=PasswordHasher.get_password_hash("Password123@12")
        )

    @patch("data_adapter.user.User.create_user")
    def test_signup_user_success(self, mock_create_user: MagicMock):
        mock_create_user.return_value = self.user
        response = UserService.signup_user(self.user_insert_data)
        self.assertEqual(response.status_code, http.HTTPStatus.CREATED)
        self.assertEqual(response.message, UserService.MSG_USER_CREATED_SUCCESS)
        self.assertEqual(response.data, self.user.build_response_model())

    @patch("data_adapter.user.User.get_active_user_by_email")
    @patch("utils.password_hasher.PasswordHasher.verify_password")
    @patch("utils.jwt_token_handler.JWTHandler.create_access_token")
    def test_login_user_success(self, mock_create_access_token: MagicMock, mock_verify_password: MagicMock,
                                mock_get_user_by_email: MagicMock):
        mock_get_user_by_email.return_value = self.user
        mock_verify_password.return_value = True
        mock_create_access_token.return_value = "test_token"
        response = UserService.login_user(self.user_login_data)
        self.assertEqual(response.status_code, http.HTTPStatus.OK)
        self.assertEqual(response.message, UserService.MSG_USER_LOGIN_SUCCESS)
        self.assertEqual(response.data.access_token, "test_token")
        self.assertEqual(response.data.user_uuid, self.user.uuid)
        self.assertEqual(response.data.user_role, self.user.role)
        self.assertEqual(response.data.user_status, self.user.status)

    @patch("data_adapter.user.User.get_active_user_by_email")
    def test_login_user_failure_user_not_found(self, mock_get_user_by_email: MagicMock):
        mock_get_user_by_email.return_value = None
        response = UserService.login_user(self.user_login_data)
        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)
        self.assertEqual(response.error, UserService.ERROR_USER_NOT_FOUND)

    @patch("data_adapter.user.User.get_active_user_by_email")
    @patch("utils.password_hasher.PasswordHasher.verify_password")
    def test_login_user_failure_invalid_credentials(self, mock_verify_password: MagicMock,
                                                    mock_get_user_by_email: MagicMock):
        mock_get_user_by_email.return_value = self.user
        mock_verify_password.return_value = False
        response = UserService.login_user(self.user_login_data)
        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)
        self.assertEqual(response.error, UserService.ERROR_INVALID_CREDENTIALS)

    def test_user_with_weak_password(self):
        with self.assertRaises(ValueError):
            UserInsertModel(
                first_name="John",
                last_name="Doe",
                email="johndoe@example.com",
                role="customer",
                status="active",
                password="Password123"
            )
        with self.assertRaises(ValueError):
            UserInsertModel(
                first_name="John",
                last_name="Doe",
                email="johndoe@example.com",
                role="customer",
                status="active",
                password="password@123"
            )
        with self.assertRaises(ValueError):
            UserInsertModel(
                first_name="John",
                last_name="Doe",
                email="johndoe@example.com",
                role="customer",
                status="active",
                password="Password@"
            )
        with self.assertRaises(ValueError):
            UserInsertModel(
                first_name="John",
                last_name="Doe",
                email="johndoe@example.com",
                role="customer",
                status="active",
                password="PASSWORD@123"
            )
        with self.assertRaises(ValueError):
            UserInsertModel(
                first_name="John",
                last_name="Doe",
                email="johndoe@example.com",
                role="customer",
                status="active",
                password="Pass@1"
            )
