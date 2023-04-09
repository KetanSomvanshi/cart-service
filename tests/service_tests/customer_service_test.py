import http
import unittest
from unittest.mock import patch

from data_adapter.user import User
from models.base import GenericResponseModel
from service.customer_service import CustomerService


class TestCustomerService(unittest.TestCase):

    def setUp(self):
        self.customer_uuid = "123"
        self.expected_error_msg = "Customer not found"
        self.expected_success_msg = "Customer is suspended successfully"

    @patch.object(User, 'update_user_by_uuid', return_value=True)
    def test_suspend_customer_success(self, mock_update_user_by_uuid):
        expected_response = GenericResponseModel(status_code=http.HTTPStatus.OK, message=self.expected_success_msg)

        response = CustomerService.suspend_customer(self.customer_uuid)

        self.assertEqual(response.status_code, expected_response.status_code)
        self.assertEqual(response.message, expected_response.message)

    @patch.object(User, 'update_user_by_uuid', return_value=False)
    def test_suspend_customer_not_found(self, mock_update_user_by_uuid):
        expected_response = GenericResponseModel(status_code=http.HTTPStatus.NOT_FOUND, error=self.expected_error_msg)

        response = CustomerService.suspend_customer(self.customer_uuid)

        self.assertEqual(response.status_code, expected_response.status_code)
        self.assertEqual(response.error, expected_response.error)
